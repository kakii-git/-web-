# backend/app/modules/user/api.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import database, security
from app.modules.user import models as user_models
from . import crud, schemas, models

router = APIRouter()

@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    ユーザー登録API
    URL: POST /users/signup
    """
    # メールアドレスの重複チェック
    # (同姓同名は許可するため、名前でのチェックは行いません)
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # DBに保存
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    # OAuth2標準フォーム (username, passwordフィールドを持つ) を使用
    # フロントエンドからは username フィールドに「メールアドレス」を入れて送信してもらう
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """
    ログインAPI
    URL: POST /users/token
    成功するとJWT（アクセストークン）を返します。
    """
    # 1. フォームのusername(中身はemail)を使ってユーザーを検索
    user = crud.get_user_by_email(db, email=form_data.username)
    
    # 2. ユーザーが存在しない、またはパスワードが一致しない場合のエラー処理
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 認証OKならトークンを発行 (subには一意なemailを入れるのが一般的)
    access_token = security.create_access_token(subject=user.email)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_info":{
            "id": user.user_id,
            "name": user.user_name,
            "email": user.email,
        }
    }

# 将来的に、アカウントの凍結を実装するときに必要
# @router.put("/{user_id}/freeze")
# def freeze_user(
#     user_id: str,
#     freeze: bool = True,  # Trueで凍結、Falseで解除
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # 1. 操作者が「システム管理者」かチェック
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=403, detail="権限がありません")

#     # 2. 対象ユーザーを取得
#     target_user = db.query(User).filter(User.user_id == user_id).first()
#     if not target_user:
#         raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

#     # 3. 凍結フラグを更新 (is_active を反転させる)
#     target_user.is_active = not freeze 
#     db.commit()

#     status_msg = "凍結しました" if freeze else "凍結解除しました"
#     return {"message": f"ユーザー {target_user.email} を{status_msg}"}