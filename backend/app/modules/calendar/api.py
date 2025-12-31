# backend/app/modules/calendar/api.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import database, security
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.calendar import models as calendar_models
from . import crud, schemas, models

router = APIRouter()