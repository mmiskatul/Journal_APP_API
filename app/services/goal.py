from datetime import datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from app.core.mongo import serialize_id, to_object_id


def create_goal(db, user: dict, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    goal = {
        "user_id": user["id"],
        "title": data["title"],
        "description": data.get("description"),
        "status": data.get("status") or "active",
        "due_date": data.get("due_date"),
        "created_at": now,
        "updated_at": now,
    }
    result = db.goals.insert_one(goal)
    goal["_id"] = result.inserted_id
    return serialize_id(goal)


def list_goals(db, user: dict) -> list[dict]:
    goals = db.goals.find({"user_id": user["id"]}).sort("created_at", -1)
    return [serialize_id(goal) for goal in goals]


def get_goal(db, user: dict, goal_id: str) -> dict:
    goal = db.goals.find_one({"_id": to_object_id(goal_id), "user_id": user["id"]})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return serialize_id(goal)


def update_goal(db, user: dict, goal_id: str, data: dict) -> dict:
    update: dict = {k: v for k, v in data.items() if v is not None}
    update["updated_at"] = datetime.now(timezone.utc)

    goal = db.goals.find_one_and_update(
        {"_id": to_object_id(goal_id), "user_id": user["id"]},
        {"$set": update},
        return_document=ReturnDocument.AFTER,
    )
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return serialize_id(goal)


def delete_goal(db, user: dict, goal_id: str) -> None:
    result = db.goals.delete_one({"_id": to_object_id(goal_id), "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
