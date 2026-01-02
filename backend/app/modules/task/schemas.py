from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

from app.modules.user.schemas import UserResponse

# --- 中間テーブル (Relation) 用 ---

class TaskUserRelationBase(BaseModel):
    is_assigned: bool = False
    reaction: str = "no-reaction"
    comment: Optional[str] = None

class TaskUserRelationResponse(TaskUserRelationBase):
    """クライアントへの返却用"""
    relation_id: str
    user_id: str
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

# --- APIリクエスト用スキーマ ---

class TaskAssignmentUpdate(BaseModel):
    """管理者による担当者任命用"""
    target_identifier: str # user_id(UUID) or email
    is_assigned: bool

class MyReactionUpdate(BaseModel):
    """自分のリアクション更新用"""
    reaction: Optional[str] = None
    comment: Optional[str] = None

# --- Task本体 ---

class TaskBase(BaseModel):
    title: str
    date: date
    time_span_begin: Optional[datetime] = None
    time_span_end: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    is_task: bool = False
    status: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[date] = None
    time_span_begin: Optional[datetime] = None
    time_span_end: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    is_task: Optional[bool] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    task_id: str
    group_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # リレーション情報（担当者や参加者）
    task_user_relations: List[TaskUserRelationResponse] = []

    class Config:
        from_attributes = True

# --- タスクテンプレート用スキーマ ---

class TaskTemplateBase(BaseModel):
    name: str  # テンプレート名
    title: str # タスクタイトル初期値
    location: Optional[str] = None
    description: Optional[str] = None

class TaskTemplateCreate(TaskTemplateBase):
    pass

class TaskTemplateResponse(TaskTemplateBase):
    template_id: str
    group_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- カレンダービュー用 軽量スキーマ ---

class CalendarTaskResponse(BaseModel):
    """月表示カレンダー用の軽量データ"""
    task_id: str
    title: str
    date: date
    time_span_begin: Optional[datetime] = None
    time_span_end: Optional[datetime] = None
    location: Optional[str] = None
    
    # 担当者情報などの重いデータは含めない

    class Config:
        from_attributes = True