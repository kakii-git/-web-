import os
from pathlib import Path
from pydantic_settings import BaseSettings

# --- ファイルパスの計算ロジック ---
# 1. このファイル (config.py) がある場所を取得
#    例: /Users/name/project/backend/src/api
BASE_DIR = Path(__file__).resolve().parent

# 2. .envファイルがある場所を計算
#    config.py から見て「3つ上の階層 (api -> src -> backend)」の外側にある .env を指す
ENV_FILE_PATH = BASE_DIR.parent.parent.parent / ".env"

# --- 設定クラスの定義 ---
class Settings(BaseSettings):
    """
    環境変数(.env)の値を読み込んで、変数の型チェックを行うクラスです。
    pydantic-settings ライブラリが自動でやってくれます。
    """
    
    # データベース接続に必要な情報
    db_user: str      # MySQLのユーザー名
    db_password: str  # MySQLのパスワード
    db_host: str = "localhost"  # サーバーの場所 (デフォルトは自分自身)
    db_port: int = 3306         # ポート番号 (MySQLの標準は3306)
    db_name: str      # データベースの名前

    # セキュリティ設定
    secret_key: str   # 暗号化に使う秘密の鍵
    algorithm: str = "HS256"  # 暗号化の方式
    access_token_expire_minutes: int = 30  # ログイン状態の有効期限(分)

    # データベース接続用URLを自動で作るプロパティ
    # 例: mysql+pymysql://root:password@localhost:3306/mydb
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # クラスの設定
    class Config:
        env_file = str(ENV_FILE_PATH)  # 読み込むファイルの場所
        extra = "ignore"  # .envの中に知らない項目があってもエラーにせず無視する

# 設定を読み込んでインスタンス化 (これを他のファイルから import して使う)
settings = Settings()