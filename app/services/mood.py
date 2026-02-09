from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.mood import MoodEntry
from app.models.user import User


def create_mood(db: Session, user: User, data: dict) -> MoodEntry:
    entry = MoodEntry(user_id=user.id, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_moods(db: Session, user: User) -> list[MoodEntry]:
    return (
        db.query(MoodEntry)
        .filter(MoodEntry.user_id == user.id)
        .order_by(MoodEntry.entry_date.desc())
        .all()
    )


def mood_stats(db: Session, user: User) -> dict:
    total_entries = db.query(MoodEntry).filter(MoodEntry.user_id == user.id).count()
    avg_intensity = (
        db.query(func.avg(MoodEntry.intensity))
        .filter(MoodEntry.user_id == user.id, MoodEntry.intensity.isnot(None))
        .scalar()
    )
    mood_counts_rows = (
        db.query(MoodEntry.mood, func.count(MoodEntry.id))
        .filter(MoodEntry.user_id == user.id)
        .group_by(MoodEntry.mood)
        .all()
    )
    mood_counts = {mood: count for mood, count in mood_counts_rows}

    return {
        "total_entries": total_entries,
        "average_intensity": float(avg_intensity) if avg_intensity is not None else None,
        "mood_counts": mood_counts,
    }
