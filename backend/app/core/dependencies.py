from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import get_db
from app.modules.user import crud as user_crud

# トークンの受け渡し場所（URL）の定義
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """
    JWTトークンを検証し、現在のユーザーを取得する依存関数
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証されていません。",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    # sub (subject) には user_id や username が入っている
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # DBからユーザーを検索
    user = user_crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    # トークンが有効でも、DB上で凍結されていたら弾く
    if not user.is_active:
        raise HTTPException(status_code=403, detail="アカウントが凍結されています。")

    return user