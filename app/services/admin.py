from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.goal import Goal
from app.models.journal import JournalEntry
from app.models.mood import MoodEntry
from app.models.subscription import Subscription
from app.models.user import User


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def suspend_user(db: Session, user_id: int, days: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.suspended_until = datetime.now(timezone.utc) + timedelta(days=days)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db: Session, user_id: int) -> str:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    temporary_password = token_urlsafe(10)
    user.hashed_password = get_password_hash(temporary_password)
    db.add(user)
    db.commit()
    return temporary_password


def analytics(db: Session) -> dict:
    return {
        "users": db.query(User).count(),
        "journals": db.query(JournalEntry).count(),
        "moods": db.query(MoodEntry).count(),
        "goals": db.query(Goal).count(),
        "active_subscriptions": db.query(Subscription).filter(Subscription.status == "active").count(),
    }
