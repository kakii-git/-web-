import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from jose import jwt

from .config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文のパスワードと、DB内のハッシュ化パスワードが一致するか検証
    bcryptは bytes型 を要求するため、.encode('utf-8') で変換してから渡す。
    """
    # DBから来た hashed_password が文字列なら bytes に変換
    if isinstance(hashed_password, str):
        hashed_password_bytes = hashed_password.encode('utf-8')
    else:
        hashed_password_bytes = hashed_password

    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)

def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化して文字列で返す
    """
    # 1. パスワードをバイト列に変換
    pwd_bytes = password.encode('utf-8')

    # 2. ソルトを生成してハッシュ化
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)

    # 3. DBに保存しやすいように文字列にデコードして返す
    return hashed_bytes.decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    JWTアクセストークンを生成する
    subject: トークンに埋め込む識別子（通常は user_id や username）
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # ペイロード（中身）の作成
    to_encode = {"sub": str(subject), "exp": expire}
    
    # 暗号化
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt