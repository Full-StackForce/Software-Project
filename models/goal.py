from dataclasses import dataclass
from datetime import date


@dataclass
class Goal:
    id: int
    user_id: int
    title: str
    description: str
    due_date: date | None
    completed: bool
