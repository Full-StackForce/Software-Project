from dataclasses import dataclass
from datetime import datetime


@dataclass
class Workout:
    id: int
    user_id: int
    type: str
    duration_minutes: int
    calories_burned: int
    notes: str | None
    completed_at: datetime
