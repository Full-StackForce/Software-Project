from dataclasses import dataclass
from datetime import date


@dataclass
class Goal:
    id: int
    user_id: int
    title: str
    description: str
    goal_type: str
    target_value: float
    due_date: date | None
    completed: bool