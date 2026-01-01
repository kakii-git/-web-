from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from . import models, schemas

# --- Task本体 ---

def create_task(db: Session, task_in: schemas.TaskCreate, group_id: str):
    db_task = models.Task(
        **task_in.model_dump(),
        group_id=group_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_group(db: Session, group_id: str, limit: int = 100):
    return db.query(models.Task)\
        .filter(models.Task.group_id == group_id)\
        .order_by(models.Task.date.asc())\
        .limit(limit)\
        .all()

def get_task(db: Session, task_id: str, group_id: str):
    return db.query(models.Task).filter(
        models.Task.task_id == task_id,
        models.Task.group_id == group_id
    ).first()

def update_task(db: Session, db_task: models.Task, task_update: schemas.TaskUpdate):
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: models.Task):
    db.delete(db_task)
    db.commit()

# --- Relation (担当/参加/コメント) のロジック ---

def get_relation(db: Session, task_id: str, user_id: str):
    return db.query(models.TaskUser_Relation).filter(
        models.TaskUser_Relation.task_id == task_id,
        models.TaskUser_Relation.user_id == user_id
    ).first()

def _ensure_relation(db: Session, task_id: str, user_id: str) -> models.TaskUser_Relation:
    """リレーションを取得、なければ作成して返す内部関数"""
    relation = get_relation(db, task_id, user_id)
    if not relation:
        relation = models.TaskUser_Relation(
            task_id=task_id,
            user_id=user_id,
            is_assigned=False,
            reaction="no-reaction",
            comment=None
        )
        db.add(relation)
        # flushしてIDなどを確定させるが、commitは呼び出し元に任せるかここで一区切りするか
        # ここでは後続処理があるため add の状態にしておく
    return relation

def _cleanup_relation(db: Session, relation: models.TaskUser_Relation):
    """
    条件: 担当でなく、リアクションも 'no-reaction' で、コメントも空ならレコード削除
    """
    # None対策
    comment_content = relation.comment if relation.comment else ""
    
    if (not relation.is_assigned) and \
       (relation.reaction == "no-reaction") and \
       (not comment_content.strip()):
        
        db.delete(relation)
        db.commit()
        return None # 削除されたことを示す
    else:
        db.commit()
        db.refresh(relation)
        return relation

def set_user_assignment(db: Session, task_id: str, user_id: str, is_assigned: bool):
    """管理者による担当者任命/解除"""
    relation = _ensure_relation(db, task_id, user_id)
    
    relation.is_assigned = is_assigned
    
    # 保存または削除判定
    return _cleanup_relation(db, relation)

def update_user_reaction(db: Session, task_id: str, user_id: str, reaction: Optional[str], comment: Optional[str]):
    """ユーザーによるリアクション/コメント更新"""
    relation = _ensure_relation(db, task_id, user_id)
    
    if reaction is not None:
        relation.reaction = reaction
    if comment is not None:
        # 空文字が来たらNoneにするか、そのまま空文字にするか。ここではそのまま保存しcleanupで判定
        relation.comment = comment

    # 保存または削除判定
    return _cleanup_relation(db, relation)