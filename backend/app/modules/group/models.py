from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

# 共通のBaseモデル
from app.core.database import Base

class Group(Base):
    """
    グループ本体のモデル
    一覧はユーザーに秘匿されるため、group_idとgroup_nameを知っている人のみがアクセス可能。
    """
    __tablename__ = "groups"

    # UUIDを主キーとする
    group_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # 修正: name -> group_name
    group_name = Column(String(100), nullable=False, index=True, comment="グループ名")
    
    # 修正: description は削除しました
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーション: 中間テーブル(GroupMember)を通じてUserと関連付け
    group_members = relationship(
        "GroupMember", 
        back_populates="group", 
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "app.modules.task.models.Task", 
        back_populates="group", 
        cascade="all, delete-orphan" # グループ削除時にタスクも全消去
    )
    task_templates = relationship(
        "app.modules.task.models.TaskTemplate",
        back_populates="group",
        cascade="all, delete-orphan" 
    )

class GroupMember(Base):
    """
    ユーザーとグループの中間テーブル
    - 誰が(user_id)
    - どのグループに(group_id)
    - どんな状態で(accepted, is_representative) 所属しているか
    """
    __tablename__ = "group_members"

    # 修正: id -> user_group_id
    user_group_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    group_id = Column(String(36), ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False)

    # 権限・状態フラグ
    is_representative = Column(Boolean, default=False, comment="代表者フラグ (True=代表/管理者)")
    accepted = Column(Boolean, default=False, comment="参加承認状態 (True=参加済み, False=承認待ち)")

    # 修正: created_at -> joined_at (参加/申請日時)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # リレーション設定
    # Userモデル側にも `groups = relationship("GroupMember", back_populates="user")` がある想定
    users = relationship(
        "app.modules.user.models.User", 
        back_populates="group_members"
    )
    group = relationship(
        "Group", 
        back_populates="group_members"
    )

    # user_idとgroup_idの組み合わせはユニークである必要がある
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='unique_user_group_membership'),
    )