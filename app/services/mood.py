from datetime import datetime, timezone

from app.core.mongo import serialize_id


def create_mood(db, user: dict, data: dict) -> dict:
    entry = {
        "user_id": user["id"],
        "mood": data["mood"],
        "intensity": data.get("intensity"),
        "notes": data.get("notes"),
        "entry_date": data["entry_date"],
        "created_at": datetime.now(timezone.utc),
    }
    result = db.mood_entries.insert_one(entry)
    entry["_id"] = result.inserted_id
    return serialize_id(entry)


def list_moods(db, user: dict) -> list[dict]:
    entries = db.mood_entries.find({"user_id": user["id"]}).sort("entry_date", -1)
    return [serialize_id(entry) for entry in entries]


def mood_stats(db, user: dict) -> dict:
    total_entries = db.mood_entries.count_documents({"user_id": user["id"]})

    avg_pipeline = [
        {"$match": {"user_id": user["id"], "intensity": {"$ne": None}}},
        {"$group": {"_id": None, "avg": {"$avg": "$intensity"}}},
    ]
    avg_result = list(db.mood_entries.aggregate(avg_pipeline))
    avg_intensity = avg_result[0]["avg"] if avg_result else None

    count_pipeline = [
        {"$match": {"user_id": user["id"]}},
        {"$group": {"_id": "$mood", "count": {"$sum": 1}}},
    ]
    mood_counts = {row["_id"]: row["count"] for row in db.mood_entries.aggregate(count_pipeline)}

    return {
        "total_entries": total_entries,
        "average_intensity": float(avg_intensity) if avg_intensity is not None else None,
        "mood_counts": mood_counts,
    }
