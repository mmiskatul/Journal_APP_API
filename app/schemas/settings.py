from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SettingsUpdate(BaseModel):
    notifications_enabled: bool | None = None
    privacy_mode: bool | None = None


class SettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notifications_enabled: bool
    privacy_mode: bool
    updated_at: datetime | None = None
