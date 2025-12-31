# backend/app/modules/calendar/models.py

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Calendar(Base):
    """
    【Calendarテーブル定義】
    カレンダーの基本情報を管理します。
    MySQLのテーブル定義と一致させる必要があります。
    """

    __tablename__ = "calendars"

    calendar_id = Column(String(36), primary_key=True,  default=lambda: str(uuid.uuid4()), index=True)
