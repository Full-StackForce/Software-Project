from datetime import date
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from dependencies.database import SessionLocal
from models.user import User
from models.weight_log import WeightLog
from schemas.user import UserCreate, UserUpdate


def create_user(payload: UserCreate) -> User:
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=409, detail="An account with this email already exists.")

        name = (payload.name or "Pulse User").strip() or "Pulse User"
        username = (payload.username or name.lower().replace(" ", "_")).strip() or "pulse_user"
        timezone = payload.timezone or "UTC"
        focus = payload.focus or "General Wellness"
        gender = payload.gender or "prefer_not_to_say"
        height_cm = payload.height_cm if payload.height_cm is not None else 170.0
        weight_kg = payload.weight_kg if payload.weight_kg is not None else 70.0
        target_weight_kg = payload.target_weight_kg if payload.target_weight_kg is not None else max(weight_kg - 2.0, 1.0)
        bedtime = payload.bedtime or "22:30"
        active_days = payload.active_days if payload.active_days is not None else 4
        hydration_goal = payload.hydration_goal or "2.5"

        db_user = User(
            username=username,
            email=payload.email,
            password=payload.password,
            name=name,
            timezone=timezone,
            focus=focus,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            target_weight_kg=target_weight_kg,
            bedtime=bedtime,
            active_days=active_days,
            hydration_goal=hydration_goal,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Seed the first weight log so trend analysis has an initial baseline.
        db.add(WeightLog(user_id=db_user.id, log_date=date.today(), weight_kg=weight_kg))
        db.commit()

        return db_user
    finally:
        db.close()


def list_users() -> List[User]:
    db: Session = SessionLocal()
    try:
        return db.query(User).order_by(User.id).all()
    finally:
        db.close()


def get_user(user_id: int) -> User | None:
    db: Session = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def update_user(user_id: int, payload: UserUpdate) -> User | None:
    db: Session = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        updates = payload.model_dump(exclude_unset=True)
        if "email" in updates:
            existing_user = db.query(User).filter(User.email == updates["email"], User.id != user_id).first()
            if existing_user:
                raise HTTPException(status_code=409, detail="An account with this email already exists.")

        for field_name, value in updates.items():
            setattr(db_user, field_name, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        db.close()


def delete_user(user_id: int) -> bool:
    db: Session = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True
    finally:
        db.close()
