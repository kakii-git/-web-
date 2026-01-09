# backend/app/core/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session, joinedload
from datetime import date, timedelta

from app.core.database import SessionLocal

from app.modules.task.models import Task
from app.modules.group.models import Group # Groupもインポート
from app.modules.chat import service as slack_service

def check_and_notify_tasks():
    """
    DBをチェックし、当日・1日前・7日前のタスクがあればSlack通知する
    """
    db: Session = SessionLocal()
    try:
        today = date.today()
        target_dates = {
            0: today,
            1: today + timedelta(days=1),
            7: today + timedelta(days=7),
        }

        for days_left, target_date in target_dates.items():
            # タスクを取得する際、親のGroup情報も一緒に取得 (joinedload) すると効率的
            tasks = db.query(Task)\
                .options(joinedload(Task.group))\
                .filter(Task.date == target_date)\
                .all()
            
            for task in tasks:
                # グループ情報があり、かつSlack連携済みの場合のみ通知
                if task.group and task.group.slack_bot_token and task.group.slack_channel_id:
                    slack_service.notify_reminder(
                        token=task.group.slack_bot_token,
                        channel_id=task.group.slack_channel_id,
                        task_title=task.title,
                        task_date=str(task.date),
                        start_time=str(task.start_time) if task.start_time else None,
                        end_time=str(task.end_time) if task.end_time else None,
                        days_left=days_left,
                        is_task=task.is_task
                    )
                
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # 毎日 朝 09:00 に実行
    scheduler.add_job(check_and_notify_tasks, 'cron', hour=9, minute=0)
    scheduler.start()