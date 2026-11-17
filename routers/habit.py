from dependencies.security import CurrentUser, require_owned, require_same_user
from fastapi import APIRouter, HTTPException
from typing import List

from controllers.habit_controller import create_habit, delete_habit, get_habit, list_habits_by_user, log_habit_progress, update_habit
from schemas.habit import HabitCreate, HabitLog, HabitResponse, HabitUpdate

router = APIRouter(prefix="/habits", tags=["habits"])


@router.post("/", response_model=HabitResponse)
def create_habit_route(payload: HabitCreate, user: CurrentUser):
    payload = payload.model_copy(update={"user_id": user.id})
    return create_habit(payload)


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit_route(habit_id: int, payload: HabitUpdate, user: CurrentUser):
    require_owned(get_habit(habit_id), user)
    habit = update_habit(habit_id, payload)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.post("/{habit_id}/log", response_model=HabitResponse)
def log_habit_route(habit_id: int, payload: HabitLog, user: CurrentUser):
    require_owned(get_habit(habit_id), user)
    habit = log_habit_progress(habit_id, payload)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.get("/", response_model=List[HabitResponse])
def get_habits(user: CurrentUser):
    return list_habits_by_user(user.id)


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit_route(habit_id: int, user: CurrentUser):
    return require_owned(get_habit(habit_id), user)


@router.get("/user/{user_id}", response_model=List[HabitResponse])
def get_user_habits(user_id: int, user: CurrentUser):
    require_same_user(user_id, user)
    return list_habits_by_user(user_id)


@router.delete("/{habit_id}")
def delete_habit_route(habit_id: int, user: CurrentUser):
    require_owned(get_habit(habit_id), user)
    if not delete_habit(habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"message": "Habit deleted"}
