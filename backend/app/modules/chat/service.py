from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

def send_slack_message(token: str, channel_id: str, message: str):
    """
    グループごとのトークンを使用してSlackにメッセージを送信する
    """
    if not token or not channel_id:
        # 連携されていない場合は何もしない
        return

    client = WebClient(token=token)
    
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=message
        )
    except SlackApiError as e:
        logger.error(f"Error sending message: {e.response['error']}")

def _format_time_range(start: str | None, end: str | None) -> str:
    """
    時間の表示形式を生成するヘルパー関数
    - 両方空欄 -> "未定"
    - どちらか入力あり -> "{start}～{end}" (Noneは空文字として扱う)
    """
    # Noneの場合は空文字に変換
    s = start if start else ""
    e = end if end else ""

    # 両方とも空文字の場合
    if not s and not e:
        return "未定"
    
    return f"{s}～{e}"

def notify_new_task(
        token: str, 
        channel_id: str, 
        task_title: str, 
        task_date: str, 
        start_time: str | None, 
        end_time: str | None,
        is_task: bool = True
    ):
    """
    新規タスク作成時の通知
    """
    time_display = _format_time_range(start_time, end_time)

    # ラベルの切り替え
    label = "タスク" if is_task else "予定"

    msg = (
        f"🆕 *新しい{label}が登録されました*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 *{task_title}*\n"
        f"📅 日付: {task_date}\n"
        f"🏢 時間: {time_display}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    send_slack_message(token, channel_id, msg)

def notify_reminder(
        token: str, 
        channel_id: str, 
        task_title: str, 
        task_date: str, 
        start_time: str | None, 
        end_time: str | None, 
        days_left: int,
        is_task: bool = True
    ):
    """
    リマインダー通知
    """
    prefix=""

    if is_task:
        if days_left == 0:
            prefix = "🚨 *【本日】タスクの期限です！*"
        elif days_left == 1:
            prefix = "⚠️ *【明日】タスクの期限です*"
        elif days_left == 7:
            prefix = "📅 *【来週】タスクまであと1週間です*"
        else:
            return
    else:
        if days_left == 0:
            prefix = "✨ *【本日】予定があります！*"
        elif days_left == 1:
            prefix = "🔜 *【明日】予定があります*"
        elif days_left == 7:
            prefix = "📅 *【来週】予定まであと1週間です*"
        else:
            return

    time_display = _format_time_range(start_time, end_time)

    msg = (
        f"{prefix}\n"
        f"📌 *{task_title}*\n"
        f"📅 日付: {task_date}\n"
        f"⏰ 時間: {time_display}"
    )
    send_slack_message(token, channel_id, msg)