from datetime import date
from pydantic import BaseModel


class HabitCreate(BaseModel):
    user_id: int
    name: str
    frequency: str
    target_count: int


class HabitUpdate(BaseModel):
    name: str | None = None
    frequency: str | None = None
    target_count: int | None = None
    completed_today: bool | None = None
    streak_count: int | None = None


class HabitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    frequency: str
    target_count: int
    streak_count: int
    completed_today: bool
    last_completed_date: date | None