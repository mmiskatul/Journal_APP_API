from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.journal import JournalEntry
from app.models.user import User


def create_entry(db: Session, user: User, data: dict) -> JournalEntry:
    entry = JournalEntry(user_id=user.id, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_entries(
    db: Session,
    user: User,
    start_date: date | None,
    end_date: date | None,
    category: str | None,
) -> list[JournalEntry]:
    query = db.query(JournalEntry).filter(JournalEntry.user_id == user.id)
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
    if category:
        query = query.filter(JournalEntry.category == category)
    return query.order_by(JournalEntry.entry_date.desc()).all()


def get_entry(db: Session, user: User, entry_id: int) -> JournalEntry:
    entry = db.query(JournalEntry).filter(JournalEntry.user_id == user.id, JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


def update_entry(db: Session, entry: JournalEntry, data: dict) -> JournalEntry:
    for key, value in data.items():
        if value is not None:
            setattr(entry, key, value)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def delete_entry(db: Session, entry: JournalEntry) -> None:
    db.delete(entry)
    db.commit()
