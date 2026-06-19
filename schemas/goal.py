from datetime import date
from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    user_id: int = Field(..., example=1)
    title: str = Field(..., example="Complete 5 workouts")
    description: str = Field(..., example="Build a consistent weekly routine")
<<<<<<< HEAD
=======
    goal_type: str = Field(..., example="fitness milestone")
    target_value: float = Field(..., example=5)
>>>>>>> 5e70ec39f05a257c690173135e6ffb4e86024f3d
    due_date: date | None = Field(None, example="2026-12-31")


class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
<<<<<<< HEAD
=======
    goal_type: str
    target_value: float
>>>>>>> 5e70ec39f05a257c690173135e6ffb4e86024f3d
    due_date: date | None
    completed: bool

    class Config:
<<<<<<< HEAD
        from_attributes= True
=======
        from_attributes = True
>>>>>>> 5e70ec39f05a257c690173135e6ffb4e86024f3d
