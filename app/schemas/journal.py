from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class JournalCreate(BaseModel):
    title: str
    content: str
    category: str | None = None
    entry_date: date


class JournalUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    entry_date: date | None = None


class JournalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category: str | None = None
    entry_date: date
    created_at: datetime
    updated_at: datetime | None = None
