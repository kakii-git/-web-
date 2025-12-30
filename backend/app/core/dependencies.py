from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
# ユーザー検索のために user モジュールの crud をインポート
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
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # security.py ではなく、ここで直接 jwt.decode するか、
        # あるいは security.py に decode 用の関数を作っても良いですが、
        # ここではシンプルに直接 decode します。
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # sub (subject) には user_id や username が入っているはず
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # DBからユーザーを検索
    # ※ user.crud の get_user_by_email が必要です
    user = user_crud.get_user_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception

    # 将来的に、アカウントの凍結を実装するときに必要
    # ★追加: ここで凍結チェック！
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="このアカウントは凍結されています。")

    return user