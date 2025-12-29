# backend/app/modules/user/crud.py

from sqlalchemy.orm import Session

from app.core.security import get_password_hash # パスワードハッシュ化用の関数
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    """
    メールアドレスでユーザーを検索します。
    用途: ログイン時のユーザー特定、新規登録時のメアド重複チェック。
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    新しいユーザーを作成してDBに保存します。
    """
    # 1. パスワードをハッシュ化（平文のまま保存するのは危険なため）
    hashed_password = get_password_hash(user.password)
    
    # 2. DBモデルのインスタンスを作成
    # user_id はモデル側で default=uuid.uuid4() としているので、ここで指定しなくてOKです。
    db_user = models.User(
        user_name=user.user_name,
        email=user.email,
        password_hash=hashed_password
    )
    
    # 3. セッションに追加してコミット（保存確定）
    db.add(db_user)
    db.commit()
    
    # 4. 保存されたデータ（自動生成されたuser_idなど）を再読み込みして最新状態にする
    db.refresh(db_user)
    return db_user