from datetime import datetime
from typing import List

from controllers.habit_controller import sync_system_habit_progress
from dependencies.database import SessionLocal
from models.workout import Workout
from schemas.workout import WorkoutCreate, WorkoutUpdate

def create_workout(payload: WorkoutCreate) -> Workout:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        workout = Workout(
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
        db.add(workout)
        db.commit()
        db.refresh(workout)

        user_workout_count = db.query(Workout).filter(Workout.user_id == payload.user_id).count()
        sync_system_habit_progress(payload.user_id, "workout", user_workout_count, completed_today=True)
        return workout
    finally:
        db.close()


def list_workouts() -> List[Workout]:
    db = SessionLocal()
    try:
        return db.query(Workout).order_by(Workout.completed_at.desc()).all()
    finally:
        db.close()


def list_workouts_by_user(user_id: int) -> List[Workout]:
    db = SessionLocal()
    try:
        return (
            db.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.completed_at.desc())
            .all()
        )
    finally:
        db.close()


def get_workout(workout_id: int) -> Workout | None:
    db = SessionLocal()
    try:
        return db.query(Workout).filter(Workout.id == workout_id).first()
    finally:
        db.close()


def update_workout(workout_id: int, payload: WorkoutUpdate) -> Workout | None:
    db = SessionLocal()
    try:
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            return None

        updates = payload.model_dump(exclude_unset=True)
        for field_name, value in updates.items():
            setattr(workout, field_name, value)

        db.commit()
        db.refresh(workout)
        return workout
    finally:
        db.close()


def delete_workout(workout_id: int) -> bool:
    db = SessionLocal()
    try:
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            return False

        user_id = workout.user_id
        db.delete(workout)
        db.commit()

        user_workout_count = db.query(Workout).filter(Workout.user_id == user_id).count()
        sync_system_habit_progress(user_id, "workout", user_workout_count, completed_today=(user_workout_count > 0))
        return True
    finally:
        db.close()
