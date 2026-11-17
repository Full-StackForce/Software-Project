from dependencies.security import CurrentUser, require_owned, require_same_user
from fastapi import APIRouter, HTTPException
from typing import List

from controllers.workout_controller import create_workout, delete_workout, get_workout, list_workouts_by_user, update_workout
from schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutResponse)
def create_workout_route(payload: WorkoutCreate, user: CurrentUser):
    payload = payload.model_copy(update={"user_id": user.id})
    return create_workout(payload)


@router.get("/", response_model=List[WorkoutResponse])
def get_workouts(user: CurrentUser):
    return list_workouts_by_user(user.id)


@router.get("/user/{user_id}", response_model=List[WorkoutResponse])
def get_user_workouts(user_id: int, user: CurrentUser):
    require_same_user(user_id, user)
    return list_workouts_by_user(user_id)


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout_route(workout_id: int, user: CurrentUser):
    return require_owned(get_workout(workout_id), user)


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout_route(workout_id: int, payload: WorkoutUpdate, user: CurrentUser):
    require_owned(get_workout(workout_id), user)
    workout = update_workout(workout_id, payload)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.delete("/{workout_id}")
def delete_workout_route(workout_id: int, user: CurrentUser):
    require_owned(get_workout(workout_id), user)
    if not delete_workout(workout_id):
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Workout deleted"}
