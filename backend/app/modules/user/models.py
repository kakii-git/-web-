# backend/app/modules/user/models.py

import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """
    【Userテーブル定義】
    ユーザーの基本情報を管理します。
    MySQLのテーブル定義と一致させる必要があります。
    """
    __tablename__ = "users"

    # --- カラム定義 ---

    # user_id: プライマリキー。UUID (String型) を使用。
    # default=lambda: str(uuid.uuid4()) により、Python側でINSERT文を作る瞬間に
    # 自動でランダムなUUID文字列を生成してセットします。
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # user_name: 表示用の名前。
    # 重複を許可するため、unique=True は付けません。
    user_name = Column(String(255), index=True, nullable=False)
    
    # email: ログインIDとして使用するため、重複不可 (unique=True) とします。
    # 必須項目 (nullable=False) です。
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # hashed_password: 生パスワードではなく、ハッシュ化（暗号化）された文字列を保存します。
    hashed_password = Column(String(255), nullable=False)
    
    # created_at: 作成日時。DBサーバーの現在時刻(func.now())をデフォルト値にします。
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # updated_at: 更新日時。データ更新時に自動で現在時刻が入ります(onupdate)。
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ★追加: スーパーユーザー権限フラグ
    # default=False により、何も指定せずに作成されたユーザーは自動的に False (一般) になります
    is_superuser = Column(Boolean, default=False, nullable=False)
    # アカウント有効フラグ (True=通常, False=凍結)
    # デフォルトはTrue(有効)。Falseにするとログインできなくなります。
    is_active = Column(Boolean, default=True, nullable=False)

    # --- リレーション定義 (テーブル間の繋がり) ---
    # 所属するグループ情報（GroupMemberテーブル）へのリンク。
    # 重要: ここで `from app.modules.group.models import GroupMember` と書いてimportすると、
    # 向こうもUserをimportしているため「循環参照エラー」になります。
    # これを防ぐため、"app.modules.group.models.GroupMember" という「文字列」で指定します。
    group_members = relationship(
        "app.modules.group.models.GroupMember", 
        back_populates="users", 
        # ユーザーが削除されたら、紐付いている group_members も一緒に破棄する設定
        cascade="all, delete-orphan" # <--- これが重要
    )
    task_user_relations = relationship(
        "app.modules.task.models.TaskUser_Relation", 
        back_populates="user", 
        # ユーザーが削除されたら、紐付いている task_user_relations も一緒に破棄する設定
        cascade="all, delete-orphan" # <--- これが重要
    )
