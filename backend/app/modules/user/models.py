# backend/app/modules/user/models.py

import uuid
from sqlalchemy import Column, String, DateTime
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
    
    # password_hash: 生パスワードではなく、ハッシュ化（暗号化）された文字列を保存します。
    password_hash = Column(String(255), nullable=False)
    
    # created_at: 作成日時。DBサーバーの現在時刻(func.now())をデフォルト値にします。
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # updated_at: 更新日時。データ更新時に自動で現在時刻が入ります(onupdate)。
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- リレーション定義 (テーブル間の繋がり) ---

    # 将来的に、アカウントの凍結を実装するときに必要
    # # ★追加: システム管理者権限 (グループの代表者とは別格の権限)
    # is_superuser = Column(Boolean, default=False)
    # # ★追加: アカウントが有効かどうか (Falseなら凍結)
    # is_active = Column(Boolean, default=True)   

    # 所属するグループ情報（UserGroupテーブル）へのリンク。
    # 重要: ここで `from app.modules.group.models import UserGroup` と書いてimportすると、
    # 向こうもUserをimportしているため「循環参照エラー」になります。
    # これを防ぐため、"app.modules.group.models.UserGroup" という「文字列」で指定します。
    groups = relationship("app.modules.group.models.UserGroup", back_populates="user")