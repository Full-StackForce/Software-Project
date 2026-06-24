from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="strongpassword")
    timezone: Optional[str] = None
    focus: Optional[str] = None
    bedtime: Optional[str] = None
    active_days: Optional[int] = None
    hydration_goal: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: Optional[str] = None
    timezone: Optional[str] = None
    focus: Optional[str] = None
    bedtime: Optional[str] = None
    active_days: Optional[int] = None
    hydration_goal: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
