from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# --- 基本パーツ ---

class UserGroupBase(BaseModel):
    is_representative: bool
    accepted: bool

# --- アクション用スキーマ ---

class GroupCreate(BaseModel):
    """グループ新規作成用"""
    # 修正: name -> group_name
    group_name: str = Field(..., min_length=1, max_length=100, description="グループ名")

class GroupJoin(BaseModel):
    """
    グループ加入申請用
    修正: 誤操作防止のため、IDと名前の両方を要求する
    """
    group_id: str = Field(..., description="参加したいグループのID")
    group_name: str = Field(..., description="参加したいグループの名前(確認用)")

# === 【追加】加入申請処理用スキーマ ===
class GroupRequestAction(BaseModel):
    """
    管理者が加入申請を処理するためのスキーマ
    """
    # UUID(ID) または Email が入力される想定
    target_identifier: str = Field(..., description="対象ユーザーのID(UUID) または Email")
    
    # アクション: approve(承認) または reject(拒否)
    action: str = Field(..., pattern="^(approve|reject)$", description="'approve' または 'reject'")


class MemberStatusUpdate(BaseModel):
    """
    メンバーの状態更新用（管理者が使用）
    - 加入許可(accepted=True)
    - 管理者任命(is_representative=True)
    """
    accepted: Optional[bool] = None
    is_representative: Optional[bool] = None

# --- レスポンス用 ---

class GroupMemberResponse(BaseModel):
    """グループ内のメンバー情報表示用"""
    user_id: str
    user_name: str # Userモデルからjoinして取得する想定
    email: EmailStr
    is_representative: bool
    accepted: bool
    joined_at: datetime

    class Config:
        from_attributes = True

class GroupResponse(BaseModel):
    """グループ詳細情報"""
    group_id: str
    group_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    # 自分自身の状態（フロントエンドでの表示制御に便利）
    my_status: Optional[UserGroupBase] = None

    class Config:
        from_attributes = True