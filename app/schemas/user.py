from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None = None
    bio: str | None = None
    timezone: str | None = None
    avatar_url: str | None = None


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    timezone: str | None = None
    avatar_url: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    is_premium: bool
    created_at: datetime
    profile: UserProfileOut | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
