from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime as _datetime, date as _date, timezone, timedelta
from enum import Enum

from app.modules.user.schemas import UserResponse

# 日本時間の定義
JST = timezone(timedelta(hours=9), 'JST')

# --- 中間テーブル (Relation) 用 ---
class TaskFilterType(str, Enum):
    my_related = "my_related"
    undecided = "undecided"
    recent_created = "recent_created"

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
    date: _date
    time_span_begin: Optional[_datetime] = None
    time_span_end: Optional[_datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    is_task: bool = False
    status: str

    @field_validator('time_span_begin', 'time_span_end')
    @classmethod
    def force_jst(cls, v: _datetime):
        if v is None:
            return None
        if v.tzinfo is None:
            return v.replace(tzinfo=JST)
        return v.astimezone(JST)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[_date] = None
    time_span_begin: Optional[_datetime] = None
    time_span_end: Optional[_datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    is_task: Optional[bool] = None
    status: Optional[str] = None

    @field_validator('time_span_begin', 'time_span_end')
    @classmethod
    def force_jst(cls, v: _datetime):
        if v is None:
            return None
        if v.tzinfo is None:
            return v.replace(tzinfo=JST)
        return v.astimezone(JST)

class TaskResponse(TaskBase):
    task_id: str
    group_id: str
    created_at: _datetime
    updated_at: Optional[_datetime] = None
    
    # リレーション情報（担当者や参加者）
    task_user_relations: List[TaskUserRelationResponse] = []

    class Config:
        from_attributes = True
    @field_serializer('time_span_begin', 'time_span_end')
    def serialize_dt(self, dt: _datetime | None, _info):
        """
        レスポンスをJSONにする直前に呼ばれます。
        UTCの時間を JST (+09:00) に変換して返します。
        """
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.astimezone(JST)
        return dt.replace(tzinfo=JST)

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
    created_at: _datetime

    class Config:
        from_attributes = True

# --- カレンダービュー用 軽量スキーマ ---

class CalendarTaskResponse(BaseModel):
    """月表示カレンダー用の軽量データ"""
    task_id: str
    title: str
    date: _date
    time_span_begin: Optional[_datetime] = None
    time_span_end: Optional[_datetime] = None
    location: Optional[str] = None
    
    # 担当者情報などの重いデータは含めない

    class Config:
        from_attributes = True

    @field_serializer('time_span_begin', 'time_span_end')
    def serialize_dt(self, dt: _datetime | None, _info):
        """
        レスポンスをJSONにする直前に呼ばれます。
        UTCの時間を JST (+09:00) に変換して返します。
        """
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.astimezone(JST)
        return dt.replace(tzinfo=JST)

# グループ横断カレンダー表示用の軽量スキーマ
class GlobalCalendarTaskResponse(BaseModel):
    task_id: str
    group_name: str  # グループ名を追加
    title: str
    date: _date
    time_span_begin: Optional[_datetime] = None
    time_span_end: Optional[_datetime] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True

    @field_serializer('time_span_begin', 'time_span_end')
    def serialize_dt(self, dt: _datetime | None, _info):
        """
        レスポンスをJSONにする直前に呼ばれます。
        UTCの時間を JST (+09:00) に変換して返します。
        """
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.astimezone(JST)
        return dt.replace(tzinfo=JST)