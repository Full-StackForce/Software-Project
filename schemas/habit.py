from datetime import date
from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    user_id: int = Field(..., example=1)
    name: str = Field(..., example="Drink water")
    description: str | None = Field(None, example="Drink 8 cups throughout the day")
    category: str = Field(default="custom", example="wellness")
    unit: str = Field(default="count", example="cups")
    track_method: str = Field(default="numeric", example="numeric")
    frequency: str = Field(..., example="daily")
    target_value: float = Field(..., example=8)


class HabitUpdate(BaseModel):
    name: str | None = Field(None, example="Drink water")
    description: str | None = Field(None, example="Drink 8 cups throughout the day")
    category: str | None = Field(None, example="wellness")
    unit: str | None = Field(None, example="cups")
    track_method: str | None = Field(None, example="numeric")
    frequency: str | None = Field(None, example="daily")
    target_value: float | None = Field(None, example=8)
    current_value: float | None = Field(None, example=4)
    completed_today: bool | None = Field(None, example=True)
    streak_count: int | None = Field(None, example=3)


class HabitLog(BaseModel):
    amount: float | None = Field(None, example=1)
    value: float | None = Field(None, example=6.5)
    completed_today: bool | None = Field(None, example=True)


class HabitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str | None
    slug: str
    category: str
    unit: str
    track_method: str
    frequency: str
    target_value: float
    current_value: float
    streak_count: int
    completed_today: bool
    last_completed_date: date | None

    class Config:
        from_attributes= True
