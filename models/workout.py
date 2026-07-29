from dataclasses import dataclass
from datetime import datetime


@dataclass
class Workout:
    id: int
    user_id: int
    type: str
    date: datetime
    start_time: time
    duration_minutes: int
    calories_burned: int | None
    notes: str | None
    mood: str | None
    mood_level: int
    completed_at: datetime

