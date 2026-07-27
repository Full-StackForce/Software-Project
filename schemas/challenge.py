from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel


class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    xp_reward: int
    target_value: Optional[float] = None
    unit: Optional[str] = None
    challenge_type: str

    class Config:
        from_attributes = True


class ChallengeStreakResponse(BaseModel):
    challenge_id: int
    title: str
    current_streak: int
    completed_today: bool


class ChallengeCompleteResponse(BaseModel):
    message: str
    challenge_id: int
    completion_date: date_type
    current_streak: int
    xp_awarded: int