from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_reset_token, get_password_hash, verify_password
from app.models.password_reset import PasswordResetToken
from app.models.settings import UserSettings
from app.models.user import User, UserProfile


def register_user(db: Session, email: str, password: str) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, hashed_password=get_password_hash(password))
    profile = UserProfile()
    settings = UserSettings()
    user.profile = profile
    user.settings = settings

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    user.last_login = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    return user


def create_login_token(user: User) -> str:
    return create_access_token(str(user.id), user.is_admin, user.is_premium)


def start_password_reset(db: Session, email: str) -> str | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    token = create_reset_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
    reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at, used=False)
    db.add(reset_token)
    db.commit()

    return token


def reset_password(db: Session, token: str, new_password: str) -> None:
    reset_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if not reset_record or reset_record.used:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if reset_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token expired")

    user = db.get(User, reset_record.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    reset_record.used = True

    db.add(user)
    db.add(reset_record)
    db.commit()
