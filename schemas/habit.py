from datetime import date
from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    user_id: int = Field(..., example=1)
    name: str = Field(..., example="Drink water")
    frequency: str = Field(..., example="daily")
    target_count: int = Field(..., example=8)


class HabitUpdate(BaseModel):
    completed_today: bool = Field(..., example=True)
    streak_count: int = Field(..., example=3)


class HabitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    frequency: str
    target_count: int
    streak_count: int
    completed_today: bool
    last_completed_date: date | None

    class Config:
        from_attributes= True
