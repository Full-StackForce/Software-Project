from datetime import datetime
import re
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


BEDTIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class UserCreate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="strongpassword")
    timezone: Optional[str] = Field(None, min_length=2, max_length=100)
    focus: Optional[str] = Field(None, min_length=3, max_length=255)
    gender: Optional[Literal["female", "male", "non-binary", "prefer_not_to_say"]] = Field(None, example="female")
    height_cm: Optional[float] = Field(None, gt=0, le=300, example=170)
    weight_kg: Optional[float] = Field(None, gt=0, le=600, example=65)
    target_weight_kg: Optional[float] = Field(None, gt=0, le=600, example=60)
    bedtime: Optional[str] = None
    active_days: Optional[int] = Field(None, ge=1, le=7)
    hydration_goal: Optional[str] = None

    @field_validator("name", "username", mode="before")
    @classmethod
    def strip_name_like_values(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("bedtime")
    @classmethod
    def validate_bedtime(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        if not BEDTIME_PATTERN.match(value):
            raise ValueError("Bedtime must use HH:MM 24-hour format (for example 22:30).")
        return value

    @field_validator("hydration_goal")
    @classmethod
    def validate_hydration_goal(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        try:
            liters = float(value)
        except ValueError as exc:
            raise ValueError("Hydration goal must be a number in liters (for example 2.5).") from exc

        if liters <= 0:
            raise ValueError("Hydration goal must be greater than 0 liters.")

        return str(liters)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, example="user@example.com")
    password: Optional[str] = Field(None, min_length=6, example="strongpassword")
    timezone: Optional[str] = Field(None, min_length=2, max_length=100)
    focus: Optional[str] = Field(None, min_length=3, max_length=255)
    gender: Optional[Literal["female", "male", "non-binary", "prefer_not_to_say"]] = Field(None, example="female")
    height_cm: Optional[float] = Field(None, gt=0, le=300, example=170)
    weight_kg: Optional[float] = Field(None, gt=0, le=600, example=65)
    target_weight_kg: Optional[float] = Field(None, gt=0, le=600, example=60)
    bedtime: Optional[str] = None
    active_days: Optional[int] = Field(None, ge=1, le=7)
    hydration_goal: Optional[str] = None

    @field_validator("name", "username", mode="before")
    @classmethod
    def strip_update_name_like_values(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("bedtime")
    @classmethod
    def validate_update_bedtime(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        if not BEDTIME_PATTERN.match(value):
            raise ValueError("Bedtime must use HH:MM 24-hour format (for example 22:30).")
        return value

    @field_validator("hydration_goal")
    @classmethod
    def validate_update_hydration_goal(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        try:
            liters = float(value)
        except ValueError as exc:
            raise ValueError("Hydration goal must be a number in liters (for example 2.5).") from exc

        if liters <= 0:
            raise ValueError("Hydration goal must be greater than 0 liters.")

        return str(liters)


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
    target_weight_kg: Optional[float] = None
    bedtime: Optional[str] = None
    active_days: Optional[int] = None
    hydration_goal: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
