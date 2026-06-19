from datetime import datetime
from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    user_id: int = Field(..., example=1)
    type: str = Field(..., example="Cardio")
    duration_minutes: int = Field(..., example=45)
    calories_burned: int = Field(..., example=320)
    notes: str | None = Field(None, example="Morning run around the park")
    mood_level: int = Field(ge=1, le=5)


class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    type: str
    duration_minutes: int
    calories_burned: int
    notes: str | None
    completed_at: datetime
    mood_level: int

    class Config:
        from_attributes= True
