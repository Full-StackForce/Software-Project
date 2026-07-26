from datetime import datetime
from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    user_id: int = Field(..., example=1)
    type: str = Field(..., example="Cardio")
    duration_minutes: int = Field(..., example=45)
    calories_burned: int| None = Field(None, example=320)
    notes: str | None = Field(None, example="Morning run around the park")
    mood_level: int = Field(ge=1, le=5)


class WorkoutUpdate(BaseModel):
    type: str | None = Field(None, example="Strength")
    duration_minutes: int | None = Field(None, example=50)
    calories_burned: int | None = Field(None, example=350)
    notes: str | None = Field(None, example="Evening gym session")
    mood_level: int | None = Field(None, ge=1, le=5)


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
