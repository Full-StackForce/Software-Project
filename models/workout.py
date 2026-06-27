from dataclasses import dataclass
from datetime import datetime


@dataclass
class Workout:
    id: int
    user_id: int
    type: str
    duration_minutes: int
    calories_burned: float
    notes: str | None
    mood_level: int
    intensity_level: int
    completed_at: datetime

