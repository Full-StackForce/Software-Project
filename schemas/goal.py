from datetime import date
from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    user_id: int = Field(..., example=1)
    title: str = Field(..., example="Complete 5 workouts")
    description: str = Field(..., example="Build a consistent weekly routine")
    due_date: date | None = Field(None, example="2026-12-31")


class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    due_date: date | None
    completed: bool

    class Config:
        from_attributes= True
