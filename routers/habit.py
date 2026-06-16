from fastapi import APIRouter, HTTPException
from typing import List

from controllers.habit_controller import create_habit, list_habits, update_habit
from schemas.habit import HabitCreate, HabitResponse, HabitUpdate

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("/", response_model=HabitResponse)
def create_habit_route(payload: HabitCreate):
    return create_habit(payload)


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit_route(habit_id: int, payload: HabitUpdate):
    habit = update_habit(habit_id, payload)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.get("/", response_model=List[HabitResponse])
def get_habits():
    return list_habits()
