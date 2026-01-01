from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.user.models import User
from app.modules.group import crud as group_crud
from app.modules.user import models as user_models # ユーザー検索用

from . import crud, schemas, models

router = APIRouter(
    prefix="/groups/{group_id}/tasks",
    tags=["Tasks"]
)

# --- 権限チェック関数 (依存関係回避のためローカル定義) ---

def check_group_member(db: Session, group_id: str, user_id: str):
    """
    一般メンバーチェック
    （タスクの閲覧、作成、自分のリアクション更新用）
    """
    member = group_crud.get_user_group(db, user_id, group_id)
    if not member or not member.accepted:
        raise HTTPException(status_code=403, detail="Not a group member")

def check_group_admin_permission(current_user: User, group_id: str, db: Session):
    """
    操作しているユーザーが、そのグループの「承認済み管理者(代表者)」かチェックする
    （担当者任命などの管理者操作用）
    """
    member_record = group_crud.get_user_group(db, current_user.user_id, group_id)
    
    # UserGroupモデルの定義に合わせて is_representative をチェック
    if not member_record or not member_record.accepted or not member_record.is_representative:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="この操作を行う権限がありません（管理者権限が必要です）。"
        )
    return member_record

def get_user_by_identifier(db: Session, identifier: str) -> User:
    """UUIDまたはEmailからユーザーを特定する内部関数"""
    from uuid import UUID
    is_uuid = False
    try:
        UUID(str(identifier))
        is_uuid = True
    except ValueError:
        is_uuid = False

    if is_uuid:
        return db.query(user_models.User).filter(user_models.User.user_id == identifier).first()
    else:
        return db.query(user_models.User).filter(user_models.User.email == identifier).first()

# --- タスク基本 CRUD ---

@router.post("/", response_model=schemas.TaskResponse)
def create_task(
    group_id: str,
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    タスクを作成する。
    ※作成者自身はメンバー(担当/参加)には追加されません。
    """
    check_group_member(db, group_id, current_user.user_id)
    
    new_task = crud.create_task(db, task_in, group_id)
    return new_task

@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_group_member(db, group_id, current_user.user_id)
    return crud.get_tasks_by_group(db, group_id)

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task_detail(
    group_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_group_member(db, group_id, current_user.user_id)
    task = crud.get_task(db, task_id, group_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    group_id: str,
    task_id: str,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_group_member(db, group_id, current_user.user_id)
    task = crud.get_task(db, task_id, group_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db, task, task_in)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    group_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # タスク削除: ここではメンバーなら誰でも削除可としていますが、
    # 管理者のみにしたい場合は check_group_admin_permission(current_user, group_id, db) に変えてください
    check_group_member(db, group_id, current_user.user_id)
    
    task = crud.get_task(db, task_id, group_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task)
    return

# --- 担当者任命 (管理者のみ) ---

@router.put("/{task_id}/assignments", response_model=schemas.TaskUserRelationResponse)
def manage_assignment(
    group_id: str,
    task_id: str,
    assignment_in: schemas.TaskAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    【管理者専用】
    特定のユーザーを担当者に任命する、または解除する。
    """
    # 1. 権限チェック (ご提示の関数を使用)
    check_group_admin_permission(current_user, group_id, db)

    # 2. タスク存在確認
    task = crud.get_task(db, task_id, group_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 3. 対象ユーザー特定
    target_user = get_user_by_identifier(db, assignment_in.target_identifier)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 4. 対象がグループメンバーか確認
    target_member = group_crud.get_user_group(db, target_user.user_id, group_id)
    if not target_member or not target_member.accepted:
        raise HTTPException(status_code=400, detail="Target user is not a member of this group")

    # 5. 更新処理
    return crud.set_user_assignment(
        db, 
        task_id=task_id, 
        user_id=target_user.user_id, 
        is_assigned=assignment_in.is_assigned
    )

# --- 自分のリアクション・コメント更新 (全メンバー可能) ---

@router.put("/{task_id}/reaction", response_model=schemas.TaskUserRelationResponse)
def update_my_reaction(
    group_id: str,
    task_id: str,
    reaction_in: schemas.MyReactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    自分の「リアクション(参加意思)」や「コメント」を更新する。
    """
    check_group_member(db, group_id, current_user.user_id)
    
    task = crud.get_task(db, task_id, group_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return crud.update_user_reaction(
        db, 
        task_id=task_id, 
        user_id=current_user.user_id, 
        reaction=reaction_in.reaction, 
        comment=reaction_in.comment
    )