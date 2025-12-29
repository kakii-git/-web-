from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

# config.pyで作ったデータベース接続URLを取得
SQLALCHEMY_DATABASE_URL = settings.database_url

# 1. エンジンを作成 (データベースへの接続そのものを管理するもの)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 2. セッション作成工場を作成
#    - autocommit=False: 自動で保存しない (最後に自分で db.commit() するため)
#    - autoflush=False: 自動でデータを同期しない (意図しないタイミングでの同期を防ぐ)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. モデルの親クラスを作成
#    models.py でテーブルを定義するときは、必ずこのクラスを継承する
Base = declarative_base()

# --- データベース接続用の依存関係関数 ---
def get_db():
    """
    APIのリクエストごとにデータベース接続を開き、
    処理が終わったら必ず閉じるための関数です。
    """
    db = SessionLocal() # 接続を開く
    try:
        yield db        # APIの処理に接続を貸し出す
    finally:
        db.close()      # 何があっても最後は必ず閉じる