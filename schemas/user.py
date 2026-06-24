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
    gender: Optional[str] = Field(None, example="female")
    height_cm: Optional[float] = Field(None, gt=0, example=170)
    weight_kg: Optional[float] = Field(None, gt=0, example=65)
    bedtime: Optional[str] = None
    active_days: Optional[int] = None
    hydration_goal: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = Field(None, example="user@example.com")
    password: Optional[str] = Field(None, min_length=6, example="strongpassword")
    timezone: Optional[str] = None
    focus: Optional[str] = None
    gender: Optional[str] = Field(None, example="female")
    height_cm: Optional[float] = Field(None, gt=0, example=170)
    weight_kg: Optional[float] = Field(None, gt=0, example=65)
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
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bedtime: Optional[str] = None
    active_days: Optional[int] = None
    hydration_goal: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
