from datetime import datetime, timezone

from fastapi import HTTPException

from app.core.mongo import serialize_id, to_object_id
from app.core.security import get_password_hash, verify_password


def update_profile(db, user: dict, data: dict) -> dict:
    profile = user.get("profile") or {}
    for key, value in data.items():
        if value is not None:
            profile[key] = value
    profile["updated_at"] = datetime.now(timezone.utc)

    db.users.update_one(
        {"_id": to_object_id(user["id"])},
        {"$set": {"profile": profile, "updated_at": datetime.now(timezone.utc)}},
    )

    user["profile"] = profile
    return serialize_id(user)


def change_password(db, user: dict, current_password: str, new_password: str) -> None:
    stored = db.users.find_one({"_id": to_object_id(user["id"])})
    if not stored or not verify_password(current_password, stored["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    db.users.update_one(
        {"_id": stored["_id"]},
        {"$set": {"hashed_password": get_password_hash(new_password), "updated_at": datetime.now(timezone.utc)}},
    )
