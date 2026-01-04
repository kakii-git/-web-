from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from slack_sdk import WebClient
from app.core.config import settings
from app.core.database import get_db
from app.modules.group import models as group_models

router = APIRouter(
    prefix="/chat",
    tags=["Chat Integration"]
)

@router.get("/slack/callback")
def slack_callback(
    code: str = Query(..., description="Slackから返却された認証コード"),
    state: str = Query(..., description="連携元のGroup ID"),
    db: Session = Depends(get_db)
):
    """
    Slack連携完了時のコールバック
    Redirect URI: https://localhost:8000/chat/slack/callback
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
        raise HTTPException(status_code=400, detail=f"Slack OAuth failed: {str(e)}")

    if not response["ok"]:
        error_detail = response.get("error", "Unknown error")
        raise HTTPException(status_code=400, detail=f"Slack OAuth error: {error_detail}")

    # レスポンスから情報を抽出
    access_token = response["access_token"]
    incoming_webhook = response.get("incoming_webhook", {})
    channel_id = incoming_webhook.get("channel_id")
    
    # DBに保存
    group.slack_bot_token = access_token
    group.slack_channel_id = channel_id
    db.commit()

    return {
        "message": "Slackとの連携に成功しました！", 
        "group": group.name, 
        "channel": incoming_webhook.get("channel")
    }