from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    settings = current_user.settings
    for key, value in payload.model_dump().items():
        if value is not None:
            setattr(settings, key, value)

    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
