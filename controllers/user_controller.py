from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from dependencies.database import SessionLocal
from models.user import User
from schemas.user import UserCreate


def create_user(payload: UserCreate) -> User:
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        username = payload.username or (
            payload.name.lower().replace(" ", "_") if payload.name else "pulse_user"
        )
        db_user = User(
            username=username,
            email=payload.email,
            password=payload.password,
            name=payload.name,
            timezone=payload.timezone,
            focus=payload.focus,
            bedtime=payload.bedtime,
            active_days=payload.active_days,
            hydration_goal=payload.hydration_goal,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    finally:
        db.close()


def list_users() -> List[User]:
    db: Session = SessionLocal()
    try:
        return db.query(User).order_by(User.id).all()
    finally:
        db.close()
