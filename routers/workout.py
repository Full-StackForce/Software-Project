from fastapi import APIRouter
from typing import List

from controllers.workout_controller import create_workout, list_workouts
from schemas.workout import WorkoutCreate, WorkoutResponse

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutResponse)
def create_workout_route(payload: WorkoutCreate):
    return create_workout(payload)


@router.get("/", response_model=List[WorkoutResponse])
def get_workouts():
    return list_workouts()


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout_route(workout_id: int):
    workout = get_workout(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout
