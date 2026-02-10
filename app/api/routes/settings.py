from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.settings import SettingsOut, SettingsUpdate

router = APIRouter()


@router.get("/", response_model=SettingsOut)
def get_settings(current_user=Depends(get_current_active_user)):
    return current_user.settings


@router.put("/", response_model=SettingsOut)
def update_settings(
    payload: SettingsUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    settings = current_user.get("settings") or {}
    for key, value in payload.model_dump().items():
        if value is not None:
            settings[key] = value

    from datetime import datetime, timezone
    from app.core.mongo import to_object_id

    settings["updated_at"] = datetime.now(timezone.utc)
    db.users.update_one(
        {"_id": to_object_id(current_user["id"])},
        {"$set": {"settings": settings, "updated_at": datetime.now(timezone.utc)}},
    )
    return settings
