# backend/app/modules/user/crud.py

from sqlalchemy.orm import Session

from app.core.security import get_password_hash # パスワードハッシュ化用の関数
from app.modules.group import models as group_models
from . import models, schemas

def get_user_by_email(db: Session, email: str):
    """
    メールアドレスでユーザーを検索します。
    用途: ログイン時のユーザー特定、新規登録時のメアド重複チェック。
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    新しいユーザーを作成してDBに保存します。
    """
    # 1. パスワードをハッシュ化（平文のまま保存するのは危険なため）
    hashed_password = get_password_hash(user.password)
    
    # 2. DBモデルのインスタンスを作成
    # user_id はモデル側で default=uuid.uuid4() としているので、ここで指定しなくてOKです。
    db_user = models.User(
        user_name=user.user_name,
        email=user.email,
        hashed_password=hashed_password
    )
    
    # 3. セッションに追加してコミット（保存確定）
    db.add(db_user)
    db.commit()
    
    # 4. 保存されたデータ（自動生成されたuser_idなど）を再読み込みして最新状態にする
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str):
    """
    指定されたIDのユーザーを物理削除します。
    """
    # 削除対象のユーザーを取得
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if db_user:
        db.delete(db_user)  # 削除命令
        db.commit()         # 確定
        return True
    return False

def toggle_user_active_status(db: Session, user_id: str, is_active: bool):
    """
    ユーザーの有効/無効(凍結)状態を切り替える
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user:
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user
    return None

# --- ★以下を追加: 所属グループ取得関数 ---
def get_user_joined_groups(db: Session, user_id: str):
    """
    ユーザーが所属している（または招待されている）グループ一覧を取得する。
    GroupMemberテーブルとGroupテーブルを結合して、グループ名まで取得する。
    """
    # SQLイメージ:
    # SELECT member.*, group.name 
    # FROM group_members AS member
    # JOIN groups AS group ON member.group_id = group.group_id
    # WHERE member.user_id = :user_id
    
    results = db.query(
        group_models.GroupMember,
        group_models.Group.group_name
    ).join(
        group_models.Group,
        group_models.GroupMember.group_id == group_models.Group.group_id
    ).filter(
        group_models.GroupMember.user_id == user_id
    ).all()

    # Pydanticスキーマ(UserGroupDetail)に合わせて辞書リストを作成
    group_list = []
    for member, group_name in results:
        group_list.append({
            "group_id": member.group_id,
            "group_name": group_name,
            "is_representative": member.is_representative,
            "accepted": member.accepted
        })
    
    return group_list