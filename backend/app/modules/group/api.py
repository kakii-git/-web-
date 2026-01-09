from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

# 依存関係 (プロジェクト構成に合わせて適宜調整してください)
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.user.models import User
from app.modules.user import models as user_models

from . import crud, schemas, models

# ロガーの設定
logger = logging.getLogger(__name__)

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

def get_user_by_identifier(db: Session, identifier: str) -> User:
    """
    識別子 (identifier) が UUID なのか Email なのかを自動判別し、
    対応する User オブジェクトをデータベースから検索して返す内部関数。
    """
    target_user = None
    
    # 1. UUID形式かどうかチェック
    is_uuid = False
    try:
        UUID(str(identifier))
        is_uuid = True
    except ValueError:
        is_uuid = False

    # 2. 検索実行
    if is_uuid:
        # UUIDなら user_id で検索
        target_user = db.query(user_models.User).filter(user_models.User.user_id == identifier).first()
    else:
        # UUIDでないなら email で検索
        target_user = db.query(user_models.User).filter(user_models.User.email == identifier).first()
        
    return target_user

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

@router.get("/{group_id}/members", response_model=List[schemas.GroupMemberResponse])
def get_group_members(
    group_id: str,
    accepted_only: bool = True,  # Trueなら「正式メンバー」、Falseなら「申請中リスト」を返す
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    グループのメンバー一覧を取得します。
    - ?accepted_only=true (デフォルト): 正式に加入しているメンバーのみ返す（名簿用）
    - ?accepted_only=false: 加入申請中のユーザーのみ返す（管理者による承認画面用）
    """
    # 1. 権限チェック (メンバーなら誰でも見れるか、管理者だけかは要件次第)
    # ここでは「グループに参加している人なら見れる」と仮定
    # check_group_member_permission(current_user, group_id, db) 

    # 2. クエリ作成
    query = db.query(models.GroupMember, user_models.User).join(
        user_models.User, 
        models.GroupMember.user_id == user_models.User.user_id # IDで結合
    ).filter(
        models.GroupMember.group_id == group_id
    )

    # 3. フィルタリング (正式メンバーか、申請中か)
    if accepted_only:
        query = query.filter(models.GroupMember.accepted == True)
    else:
        check_group_admin_permission(current_user, group_id, db) 
        query = query.filter(models.GroupMember.accepted == False)

    results = query.all()

    # 4. データを整形してレスポンスの形にする
    # DBからは (Memberオブジェクト, Userオブジェクト) のタプルが返ってくるので
    # それを GroupMemberResponse の形にマッピングします。
    response_list = []
    for member, user in results:
        response_list.append(schemas.GroupMemberResponse(
            user_id=user.user_id,
            user_name=user.user_name,       # User側から取得
            email=user.email,               # User側から取得
            is_representative=member.is_representative, # Member側から取得
            accepted=member.accepted,       # Member側から取得
            joined_at=member.joined_at      # Member側から取得
        ))

    return response_list

# === 加入申請の承認・拒否エンドポイント ===

@router.put("/{group_id}/join_requests", status_code=status.HTTP_200_OK)
def handle_join_request(
    group_id: str,
    action_in: schemas.GroupRequestAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ユーザーからの加入申請を処理します（管理者専用）。
    - target_identifier: ユーザーID(UUID) または Email
    - action: "approve" (承認) または "reject" (拒否/削除)
    """
    
    # 1. 権限チェック: 操作者がこのグループの管理者か？
    check_group_admin_permission(current_user, group_id, db)

    # 2. ターゲットユーザーの特定 (UUID or Email 自動判別)
    target_user = get_user_by_identifier(db, action_in.target_identifier)

    # ユーザーが見つからない場合
    if not target_user:
        raise HTTPException(
            status_code=404, 
            detail=f"指定されたユーザー({action_in.target_identifier})が見つかりません。"
        )

    # 3. CRUDに処理を委譲
    result_message = crud.process_join_request(
        db=db, 
        group_id=group_id, 
        user_id=target_user.user_id, # 特定したIDを渡す
        action=action_in.action
    )

    return {"message": result_message, "target_user": target_user.email}


@router.put("/{group_id}/members/{target_user_id}", response_model=schemas.GroupMemberResponse)
def manage_member(
    group_id: str,
    target_identifier: str,
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

    target_user = get_user_by_identifier(db, target_identifier)
    if not target_user:
        raise HTTPException(
            status_code=404, 
            detail=f"指定されたユーザー({target_identifier})が見つかりません。"
        )
    
    updated_member = crud.update_member_status(
        db=db, 
        group_id=group_id, 
        target_user_id=target_user.user_id, 
        updates=status_update
    )
    
    return schemas.GroupMemberResponse(
        user_id=target_user.user_id,
        user_name=target_user.user_name,
        email=target_user.email,
        is_representative=updated_member.is_representative,
        accepted=updated_member.accepted,
        joined_at=updated_member.joined_at
    )

@router.delete("/{group_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def leave_or_remove_member(
    group_id: str,
    target_identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    メンバーの脱退または除名。
    1. 本人が自分自身を指定 -> 「脱退」 (誰でも可能)
    2. 管理者が他人を指定 -> 「除名」 (管理者権限が必要)
    """
    
    target_user = get_user_by_identifier(db, target_identifier)

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="指定されたユーザーが見つかりません。",
        )

    target_user_id = target_user.user_id

    # 1. 自分以外を消す場合は管理者権限が必要
    if current_user.user_id != target_user_id:
        # 操作者が管理者であるかチェック
        check_group_admin_permission(current_user, group_id, db)

    # # 2. 脱退
    # crud.remove_member(db, group_id, target_user_id)

    try:
        # メンバー削除 (crudを使わず直接操作してcommitを遅らせる)
        member = db.query(models.GroupMember).filter(
            models.GroupMember.group_id == group_id,
            models.GroupMember.user_id == target_user_id
        ).first()

        if member:
            db.delete(member)
            db.flush()  # DBには送信するが、まだ確定しない

        # 残りのメンバー数を数える
        remaining_count = crud.count_members(db, group_id)

        # 誰もいなくなったら (0人なら) グループを削除(解散)
        if remaining_count == 0:
            group = crud.get_group(db, group_id)
            if group:
                # # delete_groupを呼べば、TaskなどもCascade設定で全部消えます
                # crud.delete_group(db, group)
                db.delete(group)
                logger.info(f"Group {group_id} has been automatically deleted.")
        db.commit()

    except Exception as e:
        db.rollback() # エラーが起きたら元に戻す
        logger.error(f"Error in leave_or_remove_member: {e}")
        raise HTTPException(status_code=500, detail="サーバーエラーが発生しました。")
    
    return

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group_api(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    【グループ解散】
    グループを削除します。
    実行できるのはグループの管理者（is_representative=True）のみです。
    タスク、メンバー、リアクションなど関連データは全て削除されます。
    """
    # 1. グループが存在するか確認
    group = crud.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="グループが見つかりません")

    # 2. 権限チェック
    check_group_admin_permission(current_user, group_id, db)
    # 3. 削除実行
    crud.delete_group(db, group)
    
    return # 204 No Content