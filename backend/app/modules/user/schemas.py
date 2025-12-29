# backend/app/modules/user/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- 認証トークン用 ---
class Token(BaseModel):
    """ログイン成功時に返すアクセストークンの型定義"""
    access_token: str
    token_type: str

# --- 共通の基底クラス (Base) ---
class UserBase(BaseModel):
    """
    作成時(Create)と表示時(Response)で共通して使う項目。
    コードの重複を避けるために継承元として定義します。
    """
    user_name: str
    # EmailStrを使うと、Pydanticが自動で「メールアドレスの形式かどうか」をチェックしてくれます。
    email: EmailStr

# --- ユーザー作成（入力）用 ---
class UserCreate(UserBase):
    """
    クライアント（React等）から送られてくるユーザー登録データ。
    パスワードは「入力時」にしか存在してはいけないため、ここに定義します。
    """
    password: str

# --- ユーザー情報表示（出力）用 ---
class UserResponse(UserBase):
    """
    クライアント（React等）に返すユーザーデータ。
    パスワードフィールドはセキュリティ上、絶対に含めてはいけません。
    代わりに、DB保存後に確定する user_id や created_at を含めます。
    """
    user_id: str   # UUIDなので文字列型(str)として定義
    created_at: datetime
    updated_at: Optional[datetime] = None # まだ更新されていなければNull許容

    class Config:
        # SQLAlchemyのモデル（DBデータ）を、そのままこのPydanticモデルに変換可能にする設定
        from_attributes = True