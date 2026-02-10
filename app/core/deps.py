from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.database import get_db
from app.core.mongo import serialize_id, to_object_id
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(db=Depends(get_db), token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        object_id = to_object_id(user_id)
    except Exception:
        raise credentials_exception

    user = db.users.find_one({"_id": object_id})
    if not user:
        raise credentials_exception

    if user.get("suspended_until") and user["suspended_until"] > datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="User is suspended")

    return serialize_id(user)


def get_current_active_user(user: dict = Depends(get_current_user)) -> dict:
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def require_admin(user: dict = Depends(get_current_active_user)) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_premium(user: dict = Depends(get_current_active_user)) -> dict:
    if not user.get("is_premium"):
        raise HTTPException(status_code=402, detail="Premium subscription required")
    return user
