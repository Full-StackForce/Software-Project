import secrets
from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from controllers.habit_controller import reset_daily_habits_for_new_day
from dependencies.database import get_db
from dependencies.security import (
    COOKIE_NAME, SESSION_SECONDS, CurrentUser, DUMMY_HASH, hash_password,
    password_hasher, require_same_user, token_digest, verify_password,
)
from models.auth_session import AuthSession
from models.login_activity import LoginActivity
from models.user import User
from schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse

router = APIRouter()


def _record_login_for_today(db: Session, user_id: int) -> bool:
    today = date.today()
    existing = db.query(LoginActivity).filter(
        LoginActivity.user_id == user_id, LoginActivity.login_date == today,
    ).first()
    if existing:
        return False
    db.add(LoginActivity(user_id=user_id, login_date=today))
    return True


def _calculate_login_streak(db: Session, user_id: int) -> int:
    login_dates = db.query(LoginActivity.login_date).filter(
        LoginActivity.user_id == user_id,
    ).order_by(LoginActivity.login_date.desc()).all()
    streak, expected_date = 0, date.today()
    for (login_date,) in login_dates:
        if login_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif login_date < expected_date:
            break
    return streak


def _user_response(db: Session, user: User) -> CurrentUserResponse:
    return CurrentUserResponse(
        user_id=user.id, name=user.name or user.username, email=user.email,
        current_streak=_calculate_login_streak(db, user.id),
    )


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        verify_password(DUMMY_HASH, credentials.password, "argon2id")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(user.password, credentials.password, user.password_scheme):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.password_scheme == "legacy_plaintext" or password_hasher.check_needs_rehash(user.password):
        user.password = hash_password(credentials.password)
        user.password_scheme = "argon2id"

    # Preserve the existing daily-rollover behavior, using its current controller.
    # Persistence/transaction boundaries there are investigated in Step 3.
    reset_daily_habits_for_new_day(user.id)
    _record_login_for_today(db, user.id)
    old_token = request.cookies.get(COOKIE_NAME)
    if old_token:
        db.query(AuthSession).filter(AuthSession.token_hash == token_digest(old_token)).delete()
    token = secrets.token_urlsafe(32)
    db.add(AuthSession(
        token_hash=token_digest(token), user_id=user.id,
        expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(seconds=SESSION_SECONDS),
    ))
    db.commit()
    response.set_cookie(
        COOKIE_NAME, token, max_age=SESSION_SECONDS, httponly=True,
        secure=request.url.scheme == "https", samesite="strict", path="/",
    )
    return LoginResponse(message="Login successful", **_user_response(db, user).model_dump())


@router.get("/me", response_model=CurrentUserResponse)
def me(user: CurrentUser, db: Session = Depends(get_db)):
    return _user_response(db, user)


@router.get("/me/{user_id}", response_model=CurrentUserResponse)
def legacy_me(user_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    require_same_user(user_id, user)
    return _user_response(db, user)


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        db.query(AuthSession).filter(AuthSession.token_hash == token_digest(token)).delete()
        db.commit()
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="strict")
    return {"message": "Signed out"}
