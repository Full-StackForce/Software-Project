from dataclasses import dataclass
from datetime import date


@dataclass
class Habit:
    id: int
    user_id: int
    name: str
    frequency: str
    target_count: int
    streak_count: int
    completed_today: bool
    last_completed_date: date | None
