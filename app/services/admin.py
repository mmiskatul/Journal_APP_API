from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from fastapi import HTTPException
from pymongo import ReturnDocument

from app.core.mongo import serialize_id, to_object_id
from app.core.security import get_password_hash


def list_users(db) -> list[dict]:
    users = db.users.find().sort("created_at", -1)
    return [serialize_id(user) for user in users]


def suspend_user(db, user_id: str, days: int) -> dict:
    suspended_until = datetime.now(timezone.utc) + timedelta(days=days)
    user = db.users.find_one_and_update(
        {"_id": to_object_id(user_id)},
        {"$set": {"suspended_until": suspended_until}},
        return_document=ReturnDocument.AFTER,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_id(user)


def reset_user_password(db, user_id: str) -> str:
    user = db.users.find_one({"_id": to_object_id(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    temporary_password = token_urlsafe(10)
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": get_password_hash(temporary_password), "updated_at": datetime.now(timezone.utc)}},
    )
    return temporary_password


def analytics(db) -> dict:
    return {
        "users": db.users.count_documents({}),
        "journals": db.journal_entries.count_documents({}),
        "moods": db.mood_entries.count_documents({}),
        "goals": db.goals.count_documents({}),
        "active_subscriptions": db.subscriptions.count_documents({"status": "active"}),
    }
