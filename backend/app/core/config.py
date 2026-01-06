from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    """
    アプリケーション全体の設定クラス
    .env ファイルの内容を自動的に読み込みます。
    """
    # プロジェクト名
    PROJECT_NAME: str = "My Project API"
    
    # データベース接続情報 (デフォルト値は例として入れていますが、.envが優先されます)
    # MySQLを使用: mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "myapp_db"

    # JWT認証用の設定
    # ※本番環境では必ず強力なランダム文字列に変更してください (openssl rand -hex 32 等で生成)
    SECRET_KEY: str = "CHANGE_THIS_TO_A_VERY_SECURE_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # トークンの有効期限（分）

    SLACK_CLIENT_ID: str = "CHANGE_ME"
    SLACK_CLIENT_SECRET: str = "CHANGE_ME"
    SLACK_REDIRECT_URI: str = "CHANGE_ME"

    @property
    def DATABASE_URL(self) -> str:
        """SQLAlchemy用の接続文字列を生成"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # .envファイルを読みに行く設定
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        # 大文字小文字を区別しない（db_userでもDB_USERでもOKにする）
        case_sensitive = True

# インスタンス化して他のファイルから import できるようにする
settings = Settings()