from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
import sys

# パスを通す
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import context
from app.core.database import Base
from app.modules.user import models as user_models
from app.modules.group import models as group_models
from app.modules.task import models as task_models
from app.modules.calendar import models as calendar_models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    # 1. まず DATABASE_URL 環境変数があるか確認
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    
    # 2. なければ、個別の環境変数からMySQL接続文字列を組み立てる
    # (docker-compose.yml で指定した変数名に合わせる)
    user = os.getenv("MYSQL_USER", "myuser")
    password = os.getenv("MYSQL_PASSWORD", "mypassword")
    host = os.getenv("DB_HOST", "db")  # サービス名の "db"
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("MYSQL_DATABASE", "myapp_db")

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # get_section が None を返す可能性を考慮して空辞書をデフォルトにする
    configuration = config.get_section(config.config_ini_section, {})
    
    # ここで確実にURLを上書きする
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()