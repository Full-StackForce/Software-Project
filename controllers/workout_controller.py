from datetime import datetime
from typing import List

from models.workout import Workout
from schemas.workout import WorkoutCreate

_workouts: List[Workout] = []
_next_workout_id = 1


def create_workout(payload: WorkoutCreate) -> Workout:
    global _next_workout_id
    workout = Workout(
        id=_next_workout_id,
        user_id=payload.user_id,
        type=payload.type,
        duration_minutes=payload.duration_minutes,
        calories_burned=payload.calories_burned,
        notes=payload.notes,
        completed_at=datetime.utcnow(),
        mood_level=payload.mood_level,
        intensity_level=payload.intensity_level,
    )
    _workouts.append(workout)
    _next_workout_id += 1
    return workout


def get_workout(workout_id: int):
    return next((w for w in _workouts if w.id == workout_id), None)


def list_workouts() -> List[Workout]:
    return list(_workouts)