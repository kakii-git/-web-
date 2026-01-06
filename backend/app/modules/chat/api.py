from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from slack_sdk import WebClient
import logging

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.modules.user.models import User
from app.modules.group import crud as group_crud
from app.modules.group import models as group_models

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat Integration"]
)

# --- 内部ヘルパー関数: 権限チェック ---

def check_chat_admin_permission(db: Session, user_id: str, group_id: str):
    """
    ユーザーが指定されたグループの「承認済み管理者」かチェックする。
    権限がない場合は 403 Forbidden を発生させる。
    """
    # group/crud.py の関数を利用してメンバー情報を取得
    member = group_crud.get_user_group(db, user_id, group_id)
    
    # メンバーが存在しない、承認されていない、または代表者(管理者)でない場合はエラー
    if not member or not member.accepted or not member.is_representative:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="この操作を行う権限がありません（管理者権限が必要です）。"
        )
    return member

# ---  連携用URL発行 (ここで管理者権限をチェック) ---
@router.get("/auth-url")
def get_slack_auth_url(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ★ここでガードする
    check_chat_admin_permission(db, current_user.user_id, group_id)

    scopes = "chat:write,incoming-webhook"
    url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={settings.SLACK_CLIENT_ID}"
        f"&scope={scopes}"
        f"&redirect_uri={settings.SLACK_REDIRECT_URI}"
        f"&state={group_id}"
    )
    return {"url": url}

@router.get("/slack/callback")
def slack_callback(
    code: str = Query(..., description="Slackから返却された認証コード"),
    state: str = Query(..., description="連携元のGroup ID"),
    db: Session = Depends(get_db)
):
    """
    Slack連携完了時のコールバック
    """
    group_id = state
    
    # グループの存在確認
    group = db.query(group_models.Group).filter(group_models.Group.group_id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    client = WebClient()
    
    # Code を Access Token に交換
    try:
        response = client.oauth_v2_access(
            client_id=settings.SLACK_CLIENT_ID,
            client_secret=settings.SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri=settings.SLACK_REDIRECT_URI
        )
    except Exception as e:
        logger.error(f"Slack OAuth failed: {e}")
        raise HTTPException(status_code=400, detail=f"Slackとの通信に失敗しました。")

    if not response["ok"]:
        error_detail = response.get("error", "Unknown error")
        raise HTTPException(status_code=400, detail=f"Slack OAuth error: {error_detail}")

    # レスポンスから情報を抽出
    access_token = response["access_token"]
    incoming_webhook = response.get("incoming_webhook", {})
    channel_id = incoming_webhook.get("channel_id")
    channel_name = incoming_webhook.get("channel")

    if not channel_id:
        raise HTTPException(status_code=400, detail="チャンネル情報の取得に失敗しました。")

    # DBに保存
    group.slack_bot_token = access_token
    group.slack_channel_id = channel_id
    db.commit()

    return {
        "message": "Slackとの連携が完了しました！", 
        "group": group.group_name, 
        "channel": channel_name,
    }

# --- 3. 連携解除 (ここでも管理者権限をチェック) ---
@router.delete("/{group_id}")
def disconnect_slack(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ★ここでガードする
    check_chat_admin_permission(db, current_user.user_id, group_id)

    group = group_crud.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group.slack_bot_token = None
    group.slack_channel_id = None
    db.commit()
    
    return {"message": "Slack連携を解除しました。"}