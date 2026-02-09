from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    due_date: date | None = None


class GoalStatusUpdate(BaseModel):
    status: str


class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: str
    due_date: date | None = None
    created_at: datetime
    updated_at: datetime | None = None
