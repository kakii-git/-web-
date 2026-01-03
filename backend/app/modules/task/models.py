# backend/app/modules/task/models.py

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Task(Base):
    """
    【Taskテーブル定義】
    タスクの基本情報を管理します。
    MySQLのテーブル定義と一致させる必要があります。
    """

    __tablename__ = "tasks"

    task_id = Column(String(36), primary_key=True,  default=lambda: str(uuid.uuid4()), index=True)

    group_id = Column(String(36), ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)

    date = Column(Date, nullable=False)

    time_span_begin = Column(DateTime)

    time_span_end = Column(DateTime)

    location = Column(String(255))

    description = Column(Text)

    is_task = Column(Boolean, default=False, nullable=False)

    status = Column(String(255), default="未着手", comment="未着手、進行中、完了、None=タスクではない")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # グループテーブルとの関係
    group = relationship(
        "app.modules.group.models.Group",
        back_populates="tasks"
    )
    # タスクユーザーテーブルとの関係
    task_user_relations = relationship(
        "TaskUser_Relation", 
        back_populates="task",
        cascade="all, delete-orphan"
    )

class TaskUser_Relation(Base):

    __tablename__ = "task_user_relations"
    
    relation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    task_id = Column(String(36), ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    is_assigned = Column(Boolean, default=False, comment="True: 担当者, False: 担当者でない")
    reaction = Column(String(20), default="no-reaction",comment="join: 参加, absent: 不参加, undecided: 未定, no-reaction: 無反応")
    comment = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship(
        "app.modules.user.models.User",
        back_populates="task_user_relations"
    )
    task = relationship(
        "Task", 
        back_populates="task_user_relations"
    )
    # task_idとuser_idの組み合わせはユニークである必要がある
    __table_args__ = (
        UniqueConstraint('task_id', 'user_id', name='unique_task_user_membership'),
    )

# --- タスクテンプレートモデル ---
class TaskTemplate(Base):
    """
    よく使うタスクの雛形を保存するテーブル
    """
    __tablename__ = "task_templates"

    template_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    group_id = Column(String(36), ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False, comment="テンプレートの管理名（例：定例会議）")
    
    # 以下、タスク作成時にコピーされる初期値
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("app.modules.group.models.Group", back_populates="task_templates")