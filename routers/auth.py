from datetime import date, timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from dependencies.database import SessionLocal
from models.login_activity import LoginActivity
from models.user import User
from schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse

router = APIRouter()


def _record_login_for_today(db: Session, user_id: int) -> None:
    today = date.today()
    existing = (
        db.query(LoginActivity)
        .filter(LoginActivity.user_id == user_id, LoginActivity.login_date == today)
        .first()
    )
    if existing:
        return

    db.add(LoginActivity(user_id=user_id, login_date=today))
    db.commit()


def _calculate_login_streak(db: Session, user_id: int) -> int:
    login_dates = [
        login_date
        for (login_date,) in (
            db.query(LoginActivity.login_date)
            .filter(LoginActivity.user_id == user_id)
            .order_by(LoginActivity.login_date.desc())
            .all()
        )
    ]

    streak = 0
    expected_date = date.today()
    for login_date in login_dates:
        if login_date == expected_date:
            streak += 1
            expected_date = expected_date - timedelta(days=1)
        elif login_date < expected_date:
            break

    return streak


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    db: Session = SessionLocal()
    try:
        # Query user from database by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Check if password matches (plain text comparison)
        # TODO: Implement proper password hashing with bcrypt
        if user.password != credentials.password:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        _record_login_for_today(db, user.id)
        current_streak = _calculate_login_streak(db, user.id)

        display_name = user.name or user.username
        return LoginResponse(
            message="Login successful",
            user_id=user.id,
            name=display_name,
            email=user.email,
            current_streak=current_streak,
        )
    
    finally:
        db.close()


@router.get("/me/{user_id}", response_model=CurrentUserResponse)
def get_current_user(user_id: int):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        current_streak = _calculate_login_streak(db, user.id)
        display_name = user.name or user.username
        return CurrentUserResponse(user_id=user.id, name=display_name, email=user.email, current_streak=current_streak)
    finally:
        db.close()