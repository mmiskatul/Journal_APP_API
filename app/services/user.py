from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User


def update_profile(db: Session, user: User, data: dict) -> User:
    if not user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in data.items():
        if value is not None:
            setattr(user.profile, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
