from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ルーター（APIエンドポイントの集合）のインポート
from app.modules.user.api import router as user_router
from app.modules.group.api import router as group_router
from app.modules.task.api import router as group_task_router
from app.modules.task.api import me_router as my_task_router

# --- FastAPIアプリの初期化 ---
app = FastAPI(
    title="My Project API",
    description="React + FastAPI + MySQL Application",
    version="0.1.0"
)

# --- CORS (Cross-Origin Resource Sharing) の設定 ---
# React (http://localhost:3000) から FastAPI (http://localhost:8000) への
# アクセスを許可するための設定です。これがないとブラウザでエラーになります。
origins = [
    "http://localhost:3000",  # Reactのデフォルトポート
    "http://localhost:5173",  # Viteを使用している場合のデフォルトポート
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 許可するオリジン
    allow_credentials=True,      # Cookie等の信用情報の送信を許可
    allow_methods=["*"],         # 許可するHTTPメソッド (GET, POST, PUT, DELETEなど全て)
    allow_headers=["*"],         # 許可するHTTPヘッダー
)

# --- ルーターの統合 ---
# 作成したモジュールごとのルーターをここでメインアプリに登録します。
app.include_router(user_router)
app.include_router(group_router)
app.include_router(group_task_router)
app.include_router(my_task_router)

# --- ヘルスチェック用エンドポイント ---
# サーバーが動いているか確認するための簡易URL (http://localhost:8000/)
@app.get("/")
def read_root():
    return {"message": "Welcome to the API! Documentation is at /docs"}