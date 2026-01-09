from sqlalchemy import or_, desc, extract
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime

from app.modules.group import models as group_models
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

# --- 高度な検索機能 ---
def get_tasks_by_group_advanced(
    db: Session, 
    group_id: str, 
    user_id: str,
    skip: int,
    limit: int,
    from_date_str: Optional[str],
    to_date_str: Optional[str],
    filter_type: Optional[str]
):
    # ベースのクエリ: 指定グループのタスク
    query = db.query(models.Task).filter(models.Task.group_id == group_id)

    # 1. 日付範囲フィルタ
    if from_date_str:
        try:
            from_dt = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            query = query.filter(models.Task.date >= from_dt)
        except ValueError:
            pass # 形式エラーは無視またはエラーハンドリング
    if to_date_str:
        try:
            to_dt = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            # 指定日の23:59:59までを含めるため、日付+時間を調整するか、
            # 単純な日付比較ならDBの型によるが、ここでは単純比較と仮定
            query = query.filter(models.Task.date <= to_dt)
        except ValueError:
            pass

    # 2. 特殊フィルタ (filter_type)
    # JOINが必要になるケースがあるため、ここで分岐
    if filter_type == "my_related":
        # 「自分に関連」: 担当(is_assigned=True) OR 参加(reaction='join')
        # TaskUser_Relation を結合して絞り込む
        query = query.join(models.TaskUser_Relation)\
            .filter(models.TaskUser_Relation.user_id == user_id)\
            .filter(
                or_(
                    models.TaskUser_Relation.is_assigned == True,
                    models.TaskUser_Relation.reaction == "join"
                )
            )
    
    elif filter_type == "undecided":
        # 「参加未定」: reaction='undecided'
        query = query.join(models.TaskUser_Relation)\
            .filter(models.TaskUser_Relation.user_id == user_id)\
            .filter(models.TaskUser_Relation.reaction == "undecided")
            
    elif filter_type == "recent_created":
        # 「最近作成された順」: created_at 降順
        # 並び替え処理のみここで適用して、後のデフォルト並び替えを回避するフラグを立てても良いが
        # ここではクエリの order_by を上書きする形になる
        query = query.order_by(desc(models.Task.created_at))
    
    # 3. 並び替え (filter_typeで指定がなければ日付順)
    if filter_type != "recent_created":
        query = query.order_by(models.Task.date.asc())

    # 4. N+1問題対策 & ページネーション
    return query\
        .options(joinedload(models.Task.task_user_relations))\
        .offset(skip)\
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
        if field in ["title", "date", "status", "is_task"] and (value is None or value == ""):
            continue
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
    if relation:
        return relation

    try:
        with db.begin_nested():
            relation = models.TaskUser_Relation(
                task_id=task_id,
                user_id=user_id,
                is_assigned=False,
                reaction="no-reaction",
                comment=None
            )
            db.add(relation)
            db.flush() # ここでINSERTを実行し、競合があればIntegrityErrorを発生させる
            return relation
        
    except IntegrityError:
        # 競合発生 (他人が一瞬早く作成した)
        # 改めて取得する
        relation = get_relation(db, task_id, user_id)
        if not relation:
            raise # 万が一それでも取得できない場合は想定外のエラーとして投げる
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

# --- カレンダー用データ取得 ---

def get_calendar_tasks(db: Session, group_id: str, year: int, month: int):
    """
    指定された年・月のタスクを軽量に取得する。
    joinedloadなどは使わず、Taskテーブルのみから必要なカラムを取得。
    """
    return db.query(
            models.Task.task_id,
            models.Task.title,
            models.Task.date,
            models.Task.time_span_begin,
            models.Task.time_span_end,
            models.Task.location
        )\
        .filter(models.Task.group_id == group_id)\
        .filter(extract('year', models.Task.date) == year)\
        .filter(extract('month', models.Task.date) == month)\
        .order_by(models.Task.date.asc())\
        .all()

# --- グループ横断で自分のタスクを軽量取得 ---
def get_my_global_tasks(db: Session, user_id: str, year: int, month: int):
    """
    所属する全グループの中から、「担当」または「参加」しているタスクを取得。
    指定された年・月のデータを全件返す。
    必要なカラム（ID, グループ名, タイトル, 日時, 場所）のみを返す。
    """
    return db.query(
            models.Task.task_id,
            group_models.Group.name.label("group_name"), # Groupテーブルの名前を取得
            models.Task.title,
            models.Task.date,
            models.Task.time_span_begin,
            models.Task.time_span_end,
            models.Task.location
        )\
        .select_from(models.Task)\
        .join(group_models.Group, models.Task.group_id == group_models.Group.group_id)\
        .join(models.TaskUser_Relation, models.Task.task_id == models.TaskUser_Relation.task_id)\
        .filter(models.TaskUser_Relation.user_id == user_id)\
        .filter(
            or_(
                models.TaskUser_Relation.is_assigned == True,
                models.TaskUser_Relation.reaction == "join"
            )
        )\
        .filter(extract('year', models.Task.date) == year)\
        .filter(extract('month', models.Task.date) == month)\
        .order_by(models.Task.date.asc())\
        .all()

# --- タスクテンプレート用CRUD ---
def create_template(db: Session, template_in: schemas.TaskTemplateCreate, group_id: str):
    db_template = models.TaskTemplate(
        **template_in.model_dump(),
        group_id=group_id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_templates(db: Session, group_id: str):
    return db.query(models.TaskTemplate)\
        .filter(models.TaskTemplate.group_id == group_id)\
        .order_by(models.TaskTemplate.created_at.desc())\
        .all()

def delete_template(db: Session, template: models.TaskTemplate):
    db.delete(template)
    db.commit()

def get_template(db: Session, template_id: str, group_id: str):
    return db.query(models.TaskTemplate).filter(
        models.TaskTemplate.template_id == template_id,
        models.TaskTemplate.group_id == group_id
    ).first()