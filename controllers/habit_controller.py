from datetime import date, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from controllers.goal_controller import refresh_goals_for_user
from dependencies.database import SessionLocal
from models.habit import Habit
from models.user import User
from schemas.habit import HabitCreate, HabitLog, HabitUpdate

SYSTEM_HABIT_SLUGS = {"hydration", "sleep", "workout"}


def _slugify(name: str) -> str:
    return "_".join(name.strip().lower().split())


def _parse_float(value: str | None, fallback: float) -> float:
    if not value:
        return fallback
    digits = "".join(character for character in value if character.isdigit() or character == ".")
    return float(digits) if digits else fallback


def _default_habit_payloads(user: User) -> list[dict]:
    return [
        {
            "name": "Hydration",
            "slug": "hydration",
            "category": "wellness",
            "unit": "liters",
            "track_method": "numeric",
            "frequency": "daily",
            "target_value": _parse_float(user.hydration_goal, 2.5),
            "current_value": 0.0,
        },
        {
            "name": "Sleep",
            "slug": "sleep",
            "category": "recovery",
            "unit": "hours",
            "track_method": "duration",
            "frequency": "daily",
            "target_value": 8.0,
            "current_value": 0.0,
        },
        {
            "name": "Workout",
            "slug": "workout",
            "category": "fitness",
            "unit": "sessions",
            "track_method": "numeric",
            "frequency": "weekly",
            "target_value": float(user.active_days or 3),
            "current_value": 0.0,
        },
    ]


def _update_completion_state(habit: Habit, explicit_completed_today: bool | None = None) -> None:
    today = date.today()
    previously_completed = habit.completed_today

    if explicit_completed_today is not None:
        habit.completed_today = explicit_completed_today
        if habit.track_method == "checkbox":
            habit.current_value = habit.target_value if explicit_completed_today else 0.0
    else:
        if habit.track_method == "checkbox":
            habit.completed_today = habit.current_value >= 1
        else:
            habit.completed_today = habit.current_value >= habit.target_value

    if habit.completed_today and habit.last_completed_date != today:
        if habit.last_completed_date == today - timedelta(days=1):
            habit.streak_count += 1
        elif habit.last_completed_date != today:
            habit.streak_count = max(habit.streak_count, 0) + 1
        habit.last_completed_date = today
    elif not habit.completed_today and previously_completed and habit.last_completed_date == today:
        habit.last_completed_date = None
        habit.streak_count = max(habit.streak_count - 1, 0)


def _ensure_default_habits(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    existing_slugs = {
        slug for (slug,) in db.query(Habit.slug).filter(Habit.user_id == user_id).all()
    }
    created_any = False
    for payload in _default_habit_payloads(user):
        if payload["slug"] in existing_slugs:
            continue
        habit = Habit(
            user_id=user_id,
            name=payload["name"],
            slug=payload["slug"],
            category=payload["category"],
            unit=payload["unit"],
            track_method=payload["track_method"],
            frequency=payload["frequency"],
            target_value=payload["target_value"],
            current_value=payload["current_value"],
            streak_count=0,
            completed_today=False,
            last_completed_date=None,
        )
        db.add(habit)
        created_any = True
    if created_any:
        db.commit()


def _get_habit_query(db: Session, habit_id: int):
    return db.query(Habit).filter(Habit.id == habit_id)


def create_habit(payload: HabitCreate) -> Habit:
    db: Session = SessionLocal()
    try:
        _ensure_default_habits(db, payload.user_id)
        slug = _slugify(payload.name)
        existing = db.query(Habit).filter(Habit.user_id == payload.user_id, Habit.slug == slug).first()
        if existing:
            raise HTTPException(status_code=409, detail="A habit with this name already exists.")

        habit = Habit(
            user_id=payload.user_id,
            name=payload.name,
            description=payload.description,
            slug=slug,
            category=payload.category,
            unit=payload.unit,
            track_method=payload.track_method,
            frequency=payload.frequency,
            target_value=payload.target_value,
            current_value=0.0,
            streak_count=0,
            completed_today=False,
            last_completed_date=None,
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)
        refresh_goals_for_user(payload.user_id, list_habits_by_user(payload.user_id))
        return habit
    finally:
        db.close()


def update_habit(habit_id: int, payload: HabitUpdate) -> Habit | None:
    db: Session = SessionLocal()
    try:
        habit = _get_habit_query(db, habit_id).first()
        if not habit:
            return None

        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            updated_name = updates["name"]
            updated_slug = _slugify(updated_name)
            existing = db.query(Habit).filter(
                Habit.user_id == habit.user_id,
                Habit.slug == updated_slug,
                Habit.id != habit.id,
            ).first()
            if existing:
                raise HTTPException(status_code=409, detail="A habit with this name already exists.")
            habit.name = updated_name
            habit.slug = updated_slug
            del updates["name"]

        explicit_completed_today = updates.pop("completed_today", None)
        for field_name, value in updates.items():
            setattr(habit, field_name, value)

        _update_completion_state(habit, explicit_completed_today)
        db.commit()
        db.refresh(habit)
        refresh_goals_for_user(habit.user_id, list_habits_by_user(habit.user_id))
        return habit
    finally:
        db.close()


def log_habit_progress(habit_id: int, payload: HabitLog) -> Habit | None:
    db: Session = SessionLocal()
    try:
        habit = _get_habit_query(db, habit_id).first()
        if not habit:
            return None

        if payload.value is not None:
            habit.current_value = max(payload.value, 0)
        elif payload.amount is not None:
            habit.current_value = max(habit.current_value + payload.amount, 0)

        _update_completion_state(habit, payload.completed_today)

        db.commit()
        db.refresh(habit)
        refresh_goals_for_user(habit.user_id, list_habits_by_user(habit.user_id))
        return habit
    finally:
        db.close()


def list_habits() -> List[Habit]:
    db: Session = SessionLocal()
    try:
        user_ids = [user_id for (user_id,) in db.query(User.id).all()]
        for user_id in user_ids:
            _ensure_default_habits(db, user_id)
        return db.query(Habit).order_by(Habit.user_id, Habit.id).all()
    finally:
        db.close()


def list_habits_by_user(user_id: int) -> List[Habit]:
    db: Session = SessionLocal()
    try:
        _ensure_default_habits(db, user_id)
        return db.query(Habit).filter(Habit.user_id == user_id).order_by(Habit.id).all()
    finally:
        db.close()


def get_habit(habit_id: int) -> Habit | None:
    db: Session = SessionLocal()
    try:
        return _get_habit_query(db, habit_id).first()
    finally:
        db.close()


def delete_habit(habit_id: int) -> bool:
    db: Session = SessionLocal()
    try:
        habit = _get_habit_query(db, habit_id).first()
        if not habit:
            return False
        if habit.slug in SYSTEM_HABIT_SLUGS:
            raise HTTPException(status_code=400, detail="Core habits cannot be deleted.")
        user_id = habit.user_id
        db.delete(habit)
        db.commit()
        refresh_goals_for_user(user_id, list_habits_by_user(user_id))
        return True
    finally:
        db.close()


def sync_system_habit_progress(user_id: int, slug: str, value: float, completed_today: bool | None = None) -> Habit | None:
    db: Session = SessionLocal()
    try:
        _ensure_default_habits(db, user_id)
        habit = db.query(Habit).filter(Habit.user_id == user_id, Habit.slug == slug).first()
        if not habit:
            return None
        habit.current_value = max(value, 0)
        _update_completion_state(habit, completed_today)
        db.commit()
        db.refresh(habit)
        refresh_goals_for_user(user_id, list_habits_by_user(user_id))
        return habit
    finally:
        db.close()
