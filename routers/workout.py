from fastapi import APIRouter, HTTPException
from typing import List

from controllers.workout_controller import create_workout, delete_workout, get_workout, list_workouts, list_workouts_by_user, update_workout
from schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutResponse)
def create_workout_route(payload: WorkoutCreate):
    return create_workout(payload)


@router.get("/", response_model=List[WorkoutResponse])
def get_workouts():
    return list_workouts()


@router.get("/user/{user_id}", response_model=List[WorkoutResponse])
def get_user_workouts(user_id: int):
    return list_workouts_by_user(user_id)


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout_route(workout_id: int):
    workout = get_workout(workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout_route(workout_id: int, payload: WorkoutUpdate):
    workout = update_workout(workout_id, payload)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.delete("/{workout_id}")
def delete_workout_route(workout_id: int):
    if not delete_workout(workout_id):
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Workout deleted"}
