from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MoodCreate(BaseModel):
    mood: str
    intensity: int | None = None
    notes: str | None = None
    entry_date: date


class MoodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mood: str
    intensity: int | None = None
    notes: str | None = None
    entry_date: date
    created_at: datetime


class MoodStats(BaseModel):
    total_entries: int
    average_intensity: float | None = None
    mood_counts: dict[str, int]
