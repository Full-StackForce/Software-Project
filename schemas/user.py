from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., example="pulse_user")
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="strongpassword")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes= True
