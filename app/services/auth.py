from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.mongo import serialize_id, to_object_id
from app.core.security import create_access_token, create_reset_token, get_password_hash, verify_password


def register_user(db, email: str, password: str) -> dict:
    existing = db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc)
    user = {
        "email": email,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "is_admin": False,
        "is_premium": False,
        "suspended_until": None,
        "last_login": None,
        "created_at": now,
        "updated_at": now,
        "profile": {"full_name": None, "bio": None, "timezone": None, "avatar_url": None, "updated_at": now},
        "settings": {"notifications_enabled": True, "privacy_mode": False, "updated_at": now},
    }

    result = db.users.insert_one(user)
    user["_id"] = result.inserted_id
    return serialize_id(user)


def authenticate_user(db, email: str, password: str) -> dict:
    user = db.users.find_one({"email": email})
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Inactive user")

    now = datetime.now(timezone.utc)
    db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": now, "updated_at": now}})
    user["last_login"] = now
    return serialize_id(user)


def create_login_token(user: dict) -> str:
    return create_access_token(user["id"], user.get("is_admin", False), user.get("is_premium", False))


def start_password_reset(db, email: str) -> str | None:
    user = db.users.find_one({"email": email})
    if not user:
        return None

    token = create_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
    reset_token = {
        "user_id": str(user["_id"]),
        "token": token,
        "expires_at": expires_at,
        "used": False,
        "created_at": datetime.now(timezone.utc),
    }
    db.password_reset_tokens.insert_one(reset_token)

    return token


def reset_password(db, token: str, new_password: str) -> None:
    reset_record = db.password_reset_tokens.find_one({"token": token})
    if not reset_record or reset_record.get("used"):
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if reset_record["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token expired")

    user = db.users.find_one({"_id": to_object_id(reset_record["user_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": get_password_hash(new_password), "updated_at": datetime.now(timezone.utc)}},
    )
    db.password_reset_tokens.update_one({"_id": reset_record["_id"]}, {"$set": {"used": True}})
