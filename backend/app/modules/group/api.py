from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# 依存関係 (プロジェクト構成に合わせて適宜調整してください)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.user.models import User

from . import crud, schemas, models

router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

# --- 依存関数: 権限チェックロジック ---

def check_group_admin_permission(current_user: User, group_id: str, db: Session):
    """
    操作しているユーザーが、そのグループの「承認済み管理者」かチェックする
    """
    member_record = crud.get_user_group(db, current_user.user_id, group_id)
    if not member_record or not member_record.accepted or not member_record.is_representative:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="この操作を行う権限がありません（管理者権限が必要です）。"
        )
    return member_record

# --- エンドポイント ---

@router.post("/", response_model=schemas.GroupResponse, status_code=status.HTTP_201_CREATED)
def create_new_group(
    group_in: schemas.GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    団体の新規作成。作成者は自動的に管理者(accepted=True)になります。
    """
    return crud.create_group(db, group_in, current_user.user_id)


@router.post("/join", status_code=status.HTTP_200_OK)
def request_join_group(
    join_in: schemas.GroupJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    既存の団体への加入申請。
    group_id と group_name の両方が一致しないと申請できません。
    申請後は accepted=False の状態になります。
    """
    crud.join_group(db, join_in, current_user.user_id)
    return {"message": "加入申請を送信しました。管理者の承認をお待ちください。"}


@router.put("/{group_id}/members/{target_user_id}", response_model=schemas.GroupMemberResponse)
def manage_member(
    group_id: str,
    target_user_id: str,
    status_update: schemas.MemberStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    メンバーの状態変更（管理者のみ実行可能）。
    - 申請の許可 (accepted: True)
    - 管理者の任命 (is_representative: True)
    """
    # 権限チェック: 操作者が管理者であるか
    check_group_admin_permission(current_user, group_id, db)

    updated_member = crud.update_member_status(db, group_id, target_user_id, status_update)
    
    # レスポンス用にuser_nameなどを埋める必要がありますが、
    # ここでは簡易的にORMオブジェクトを返却し、response_modelのfrom_attributesに任せます。
    # 必要に応じてUserテーブルをjoinして名前を取得してください。
    return updated_member


@router.delete("/{group_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def leave_or_remove_member(
    group_id: str,
    target_user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    メンバーの脱退または除名。
    1. 本人が自分自身を指定 -> 「脱退」 (誰でも可能)
    2. 管理者が他人を指定 -> 「除名」 (管理者権限が必要)
    """
    
    # 1. 脱退 (自分自身を削除)
    if current_user.user_id == target_user_id:
        crud.remove_member(db, group_id, target_user_id)
        return

    # 2. 除名 (他者を削除)
    # 操作者が管理者であるかチェック
    check_group_admin_permission(current_user, group_id, db)
    
    crud.remove_member(db, group_id, target_user_id)
    return