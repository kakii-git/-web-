from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

# 上で作った設定をインポート
from .config import settings

# データベースエンジンの作成
# MySQLの場合、接続が切れないように pool_recycle を設定するのが定石です
engine = create_engine(
    settings.DATABASE_URL,
    pool_recycle=3600,       # 1時間ごとに接続を再利用
    pool_pre_ping=True,      # 接続前に生存確認を行う（エラー防止）
    echo=False               # SQLログを出力したい場合は True にする
)

# セッション作成クラス
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル定義のための基底クラス (各モデルはこれを継承する)
Base = declarative_base()

def get_db() -> Generator:
    """
    FastAPIの依存関係(Dependency)として使うデータベースセッション取得関数。
    リクエストの開始時にセッションを作り、完了時に必ず閉じます。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()