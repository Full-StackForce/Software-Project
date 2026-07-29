from datetime import datetime
from typing import List

from controllers.habit_controller import sync_system_habit_progress
from models.workout import Workout
from schemas.workout import WorkoutCreate, WorkoutUpdate

_workouts: List[Workout] = []
_next_workout_id = 1


def create_workout(payload: WorkoutCreate) -> Workout:
    global _next_workout_id
    now = datetime.utcnow()
    workout = Workout(
        id=_next_workout_id,
        user_id=payload.user_id,
        type=payload.type,
        date=now,
        start_time=now.time().replace(microsecond=0),
        duration_minutes=payload.duration_minutes,
        calories_burned=payload.calories_burned if payload.calories_burned is not None else 0,
        notes=payload.notes,
        mood=None,
        completed_at=now,
        mood_level=payload.mood_level,
    )
    _workouts.append(workout)
    _next_workout_id += 1
    sync_system_habit_progress(payload.user_id, "workout", len(list_workouts_by_user(payload.user_id)), completed_today=True)
    return workout


def list_workouts() -> List[Workout]:
    return list(_workouts)


def list_workouts_by_user(user_id: int) -> List[Workout]:
    return [w for w in _workouts if w.user_id == user_id]


def get_workout(workout_id: int) -> Workout | None:
    return next((workout for workout in _workouts if workout.id == workout_id), None)


def update_workout(workout_id: int, payload: WorkoutUpdate) -> Workout | None:
    workout = get_workout(workout_id)
    if not workout:
        return None

    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(workout, field_name, value)
    return workout


def delete_workout(workout_id: int) -> bool:
    for index, workout in enumerate(_workouts):
        if workout.id == workout_id:
            del _workouts[index]
            return True
    return False
