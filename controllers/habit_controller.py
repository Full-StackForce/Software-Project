from datetime import date
from typing import List

from models.habit import Habit
from schemas.habit import HabitCreate, HabitUpdate

_habits: List[Habit] = []
_next_habit_id = 1


def create_habit(payload: HabitCreate) -> Habit:
    global _next_habit_id
    habit = Habit(
        id=_next_habit_id,
        user_id=payload.user_id,
        name=payload.name,
        frequency=payload.frequency,
        target_count=payload.target_count,
        streak_count=0,
        completed_today=False,
        last_completed_date=None,
    )
    _habits.append(habit)
    _next_habit_id += 1
    return habit


def update_habit(habit_id: int, payload: HabitUpdate) -> Habit | None:
    for habit in _habits:
        if habit.id == habit_id:
            habit.completed_today = payload.completed_today
            habit.streak_count = payload.streak_count
            habit.last_completed_date = date.today()
            return habit
    return None

def delete_habit(habit_id: int) -> bool:
    global _habits

    before_count = len(_habits)
    _habits = [habit for habit in _habits if habit.id != habit_id]

    return len(_habits) < before_count


def list_habits(user_id: int) -> List[Habit]:
    return [habit for habit in _habits if habit.user_id == user_id]
