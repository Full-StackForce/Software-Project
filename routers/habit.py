from fastapi import APIRouter, HTTPException
from typing import List

from controllers.habit_controller import (
    create_habit,
    list_habits,
    update_habit,
    delete_habit,
)
from schemas.habit import HabitCreate, HabitResponse, HabitUpdate

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("/", response_model=HabitResponse)
def create_habit_route(payload: HabitCreate):
    return create_habit(payload)


@router.get("/{user_id}", response_model=List[HabitResponse])
def get_habits(user_id: int):
    return list_habits(user_id)


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit_route(habit_id: int, payload: HabitUpdate):
    habit = update_habit(habit_id, payload)

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    return habit


@router.delete("/{habit_id}")
def delete_habit_route(habit_id: int):
    deleted = delete_habit(habit_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Habit not found")

    return {"message": "Habit deleted successfully"}