from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    is_premium: bool
    suspended_until: datetime | None = None
    created_at: datetime


class SuspendRequest(BaseModel):
    days: int


class AdminResetPasswordResponse(BaseModel):
    temporary_password: str


class AnalyticsOut(BaseModel):
    users: int
    journals: int
    moods: int
    goals: int
    active_subscriptions: int


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict | None = None
    created_at: datetime
