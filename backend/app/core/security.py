from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError # JWTトークン作成用ライブラリ
from passlib.context import CryptContext # パスワードハッシュ化ライブラリ
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from . import database, crud, schemas

# 設定ファイルから秘密鍵などを読み込む
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# パスワードハッシュ化の設定 (bcryptという強力なアルゴリズムを使用)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# クライアントがトークンを送ってくる場所 (/token というURLで発行されると定義)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 関数定義 ---

def verify_password(plain_password, hashed_password):
    """入力されたパスワードと、DBにあるハッシュ化パスワードが一致するか確認"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """生のパスワードを暗号化(ハッシュ化)して返す"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """ログイン成功時に渡すJWTアクセストークンを作成する"""
    to_encode = data.copy()
    # UTC時刻で有効期限を設定
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 秘密鍵を使って署名付きトークンを作成
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    トークンを持っているユーザーだけが通れる関所のような関数。
    トークンを検証し、正しければDBからユーザー情報を取得して返す。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # トークンを復号化して中身を取り出す
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # ユーザー名でDBを検索
    user = crud.get_user_by_username(db, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    return user