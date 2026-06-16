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
