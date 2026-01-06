# backend/app/modules/user/api.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import database, security
from app.core.database import get_db
from app.core.dependencies import get_current_user
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
        raise HTTPException(status_code=400, detail="そのアドレスは無効です。")
    
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
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="入力された情報が不正です。",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. 凍結アカウントチェック
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アカウントが凍結されています。"
        )
    
    # 4. 認証OKならトークンを発行 (subには一意なemailを入れるのが一般的)
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

# === 【追加】ログアウト用エンドポイント ===
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: user_models.User = Depends(get_current_user)):
    """
    ログアウトAPI
    URL: POST /users/logout
    
    【注意】
    JWT認証はステートレス（サーバー側でセッションを持たない）であるため、
    サーバー側でトークンを無効化する処理は、ブラックリスト機能を実装しない限り行えません。
    
    このエンドポイントの主な役割は以下の通りです：
    1. クライアントに対して「ログアウト処理の受付」を完了したことを伝える
    2. 必要であれば「誰がいつログアウトしたか」をログに残す
    
    ★フロントエンド側での実装必須事項:
    このAPIを叩いた後（あるいは同時に）、必ずブラウザの LocalStorage や Cookie から
    アクセストークンを削除してください。
    """
    
    # ここにログ出力処理などを書くことができます
    # print(f"User {current_user.email} has logged out.")
    
    return {"message": "ログアウトしました。ブラウザのトークンを破棄してください。"}

@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(
    # ログイン中のユーザー情報を自動取得（トークンが必要になります）
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    ログイン中のユーザー自身のアカウントを削除します。
    """
    # crudの削除関数を呼び出す
    # success = crud.delete_user(db, user_id=current_user.user_id)
    success = crud.delete_user(db, user_id=current_user.user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした。")
    
    # 204 No Content は「成功したけど返すデータはない」という意味
    return

@router.put("/{user_id}/status", response_model=schemas.UserResponse)
def change_user_status(
    user_id: str,
    status_in: schemas.FreezeRequest,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(get_current_user)
):
    """
    【Superuser専用】
    指定したユーザーのアカウントを凍結(False)または解除(True)する。
    """
    # 権限チェック: 実行者がSuperuserでなければ拒否
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作を行う権限がありません。"
        )

    # 自分自身を凍結してしまうのを防ぐ（誤操作防止）
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="super権限者自身を凍結することはできません。"
        )

    updated_user = crud.toggle_user_active_status(db, user_id, status_in.is_active)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりませんでした。")
        
    return updated_user

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: user_models.User = Depends(get_current_user)):
    """ログイン中の自分の情報を取得"""
    return current_user

# --- ★以下を追加: 所属グループ一覧取得API ---
@router.get("/me/groups", response_model=List[schemas.UserGroupDetail])
def read_my_groups(
    current_user: user_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ログイン中のユーザーが所属している（または招待されている）グループ一覧を取得します。
    """
    return crud.get_user_joined_groups(db, user_id=current_user.user_id)