from datetime import date, datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from app.core.mongo import serialize_id, to_object_id


def create_entry(db, user: dict, data: dict) -> dict:
    now = datetime.now(timezone.utc)
    entry = {
        "user_id": user["id"],
        "title": data["title"],
        "content": data["content"],
        "category": data.get("category"),
        "entry_date": data["entry_date"],
        "created_at": now,
        "updated_at": now,
    }
    result = db.journal_entries.insert_one(entry)
    entry["_id"] = result.inserted_id
    return serialize_id(entry)


def list_entries(
    db,
    user: dict,
    start_date: date | None,
    end_date: date | None,
    category: str | None,
) -> list[dict]:
    query: dict = {"user_id": user["id"]}
    if start_date or end_date:
        query["entry_date"] = {}
        if start_date:
            query["entry_date"]["$gte"] = start_date
        if end_date:
            query["entry_date"]["$lte"] = end_date
    if category:
        query["category"] = category

    entries = db.journal_entries.find(query).sort("entry_date", -1)
    return [serialize_id(entry) for entry in entries]


def get_entry(db, user: dict, entry_id: str) -> dict:
    entry = db.journal_entries.find_one({"_id": to_object_id(entry_id), "user_id": user["id"]})
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return serialize_id(entry)


def update_entry(db, entry_id: str, user: dict, data: dict) -> dict:
    update: dict = {k: v for k, v in data.items() if v is not None}
    update["updated_at"] = datetime.now(timezone.utc)

    result = db.journal_entries.find_one_and_update(
        {"_id": to_object_id(entry_id), "user_id": user["id"]},
        {"$set": update},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return serialize_id(result)


def delete_entry(db, entry_id: str, user: dict) -> None:
    result = db.journal_entries.delete_one({"_id": to_object_id(entry_id), "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Journal entry not found")
