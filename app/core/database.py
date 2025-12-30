from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv() # .envを読み込む

# .envからDATABASE_URLを取得
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# エンジンの作成
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# セッションの作成（DB操作を行うための窓口）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル定義のベースクラス
Base = declarative_base()

# DBセッションを取得する依存関数（APIのエンドポイントで使う）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
