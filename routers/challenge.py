from typing import List

from fastapi import APIRouter
from sqlalchemy.orm import Session

from controllers import challenge_controller
from dependencies.database import SessionLocal
from schemas.challenge import (
    ChallengeResponse,
    ChallengeStreakResponse,
    ChallengeCompleteResponse,
    ChallengeStatsResponse,
    WeeklyChallengeResponse,
)

router = APIRouter(prefix="/challenges")


@router.get("/", response_model=List[ChallengeResponse])
def list_challenges():
    db: Session = SessionLocal()
    try:
        return challenge_controller.get_all_challenges(db)
    finally:
        db.close()


@router.post("/{challenge_id}/complete/{user_id}", response_model=ChallengeCompleteResponse)
def complete_challenge(challenge_id: int, user_id: int):
    db: Session = SessionLocal()
    try:
        return challenge_controller.complete_challenge(db, user_id, challenge_id)
    finally:
        db.close()


@router.get("/streaks/{user_id}", response_model=List[ChallengeStreakResponse])
def get_streaks(user_id: int):
    db: Session = SessionLocal()
    try:
        return challenge_controller.get_user_challenge_streaks(db, user_id)
    finally:
        db.close()

@router.get("/stats/{user_id}", response_model=ChallengeStatsResponse)
def get_stats(user_id: int):
    db: Session = SessionLocal()
    try:
        return challenge_controller.get_user_stats(db, user_id)
    finally:
        db.close()


@router.get("/weekly/{user_id}", response_model=List[WeeklyChallengeResponse])
def get_weekly(user_id: int):
    db: Session = SessionLocal()
    try:
        return challenge_controller.get_weekly_challenges(db, user_id)
    finally:
        db.close()


@router.post("/weekly/{challenge_id}/progress/{user_id}", response_model=WeeklyChallengeResponse)
def update_weekly(challenge_id: int, user_id: int, increment: float):
    db: Session = SessionLocal()
    try:
        return challenge_controller.update_weekly_progress(db, user_id, challenge_id, increment)
    finally:
        db.close()
        