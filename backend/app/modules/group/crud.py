from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from . import models, schemas

# --- 取得系 ---

def get_group_by_id(db: Session, group_id: str):
    """IDでグループを検索"""
    return db.query(models.Group).filter(models.Group.group_id == group_id).first()

def get_user_group(db: Session, user_id: str, group_id: str):
    """特定のユーザーとグループの結びつき(メンバー情報)を取得"""
    return db.query(models.UserGroup).filter(
        and_(models.UserGroup.user_id == user_id, models.UserGroup.group_id == group_id)
    ).first()

# --- 作成・加入系 ---
# === 【追加】申請処理ロジック ===

def process_join_request(db: Session, group_id: str, user_id: str, action: str) -> str:
    """
    加入申請を承認または拒否する
    """
    # 1. 該当するメンバーシップ（申請データ）を取得
    member = get_user_group(db, user_id, group_id)

    # データが存在しない場合
    if not member:
        raise HTTPException(status_code=404, detail="該当ユーザーからの加入申請が見つかりません。")

    # 既に承認済みの場合（二重承認の防止）
    if member.accepted:
        raise HTTPException(status_code=400, detail="このユーザーは既に参加済み(承認済み)です。")

    # 2. アクションによる分岐
    if action == "approve":
        # === 承認処理 ===
        member.accepted = True
        # 必要であればここで役職などを初期設定する (例: status="MEMBER")
        db.add(member)
        db.commit()
        db.refresh(member)
        return "加入申請を承認しました。"

    elif action == "reject":
        # === 拒否処理 ===
        # 仕様: 「データベースから削除する」
        db.delete(member)
        db.commit()
        return "加入申請を拒否(削除)しました。"
    
    else:
        # スキーマで弾いているはずだが念のため
        raise HTTPException(status_code=400, detail="不正なアクションです。")


def create_group(db: Session, group_in: schemas.GroupCreate, creator_user_id: str):
    """
    グループを新規作成し、作成者を管理者(代表)として登録
    """
    # 1. グループ作成
    db_group = models.Group(
        group_name=group_in.group_name
    )
    db.add(db_group)
    db.flush() # ID生成のためflush

    # 2. 作成者を管理者として登録 (承認済み)
    db_member = models.UserGroup(
        group_id=db_group.group_id,
        user_id=creator_user_id,
        is_representative=True, # 管理者
        accepted=True           # 参加済み
    )

    my_status_data = {
        "is_representative": True,
        "accepted": True,
    }
    setattr(db_group, "my_status", my_status_data)

    db.add(db_member)
    
    db.commit()
    db.refresh(db_group)
    return db_group

def join_group(db: Session, join_in: schemas.GroupJoin, user_id: str):
    """
    既存グループへの加入申請
    修正: group_idとgroup_nameが一致しない場合はエラーとする
    """
    target_group = get_group_by_id(db, join_in.group_id)
    
    # 1. グループ存在確認
    if not target_group:
        raise HTTPException(status_code=404, detail="指定されたグループは存在しません。")

    # 2. 名前の一致確認 (誤操作防止)
    if target_group.group_name != join_in.group_name:
        raise HTTPException(status_code=400, detail="指定されたグループは存在しません。")

    # 3. 既に参加済み/申請済みか確認
    existing_member = get_user_group(db, user_id, join_in.group_id)
    if existing_member:
        if existing_member.accepted:
            raise HTTPException(status_code=400, detail="既に参加済みのグループです。")
        else:
            raise HTTPException(status_code=400, detail="既に加入申請中です。承認をお待ちください。")

    # 4. 申請データの作成 (accepted=False, is_representative=False)
    new_member = models.UserGroup(
        group_id=join_in.group_id,
        user_id=user_id,
        is_representative=False,
        accepted=False 
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

# --- メンバー管理系 (更新・削除) ---

def update_member_status(db: Session, group_id: str, target_user_id: str, updates: schemas.MemberStatusUpdate):
    """
    メンバーの状態(承認、管理者権限)を変更する
    """
    member = get_user_group(db, target_user_id, group_id)
    if not member:
        raise HTTPException(status_code=404, detail="対象のメンバーが見つかりません。")
    
    # 指定されたフィールドのみ更新
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def remove_member(db: Session, group_id: str, target_user_id: str):
    """
    メンバーを削除する (脱退または除名)
    """
    member = get_user_group(db, target_user_id, group_id)
    if not member:
        raise HTTPException(status_code=404, detail="メンバーが見つかりません。")
    
    db.delete(member)
    db.commit()
    return True

# 人がいなくなった団体は自動で削除するようにしたい(予定)
