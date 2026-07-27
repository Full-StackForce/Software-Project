from datetime import date, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.challenge import Challenge
from models.challenge_completion import ChallengeCompletion
from models.user import User


def get_all_challenges(db: Session) -> List[Challenge]:
    return db.query(Challenge).all()


def _calculate_challenge_streak(db: Session, user_id: int, challenge_id: int) -> int:
    """Mirrors _calculate_login_streak in auth.py, scoped to one challenge."""
    completion_dates = [
        completion_date
        for (completion_date,) in (
            db.query(ChallengeCompletion.completion_date)
            .filter(
                ChallengeCompletion.user_id == user_id,
                ChallengeCompletion.challenge_id == challenge_id,
            )
            .order_by(ChallengeCompletion.completion_date.desc())
            .all()
        )
    ]

    streak = 0
    expected_date = date.today()
    for completion_date in completion_dates:
        if completion_date == expected_date:
            streak += 1
            expected_date = expected_date - timedelta(days=1)
        elif completion_date < expected_date:
            break

    return streak


def complete_challenge(db: Session, user_id: int, challenge_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    today = date.today()
    already_completed = (
        db.query(ChallengeCompletion)
        .filter(
            ChallengeCompletion.user_id == user_id,
            ChallengeCompletion.challenge_id == challenge_id,
            ChallengeCompletion.completion_date == today,
        )
        .first()
    )
    if already_completed:
        current_streak = _calculate_challenge_streak(db, user_id, challenge_id)
        return {
            "message": "Challenge already completed today",
            "challenge_id": challenge_id,
            "completion_date": today,
            "current_streak": current_streak,
            "xp_awarded": 0,
        }

    db.add(ChallengeCompletion(user_id=user_id, challenge_id=challenge_id, completion_date=today))
    db.commit()

    current_streak = _calculate_challenge_streak(db, user_id, challenge_id)

    return {
        "message": "Challenge completed",
        "challenge_id": challenge_id,
        "completion_date": today,
        "current_streak": current_streak,
        "xp_awarded": challenge.xp_reward,
    }


def get_user_challenge_streaks(db: Session, user_id: int) -> List[dict]:
    challenges = db.query(Challenge).all()
    today = date.today()
    results = []

    for challenge in challenges:
        current_streak = _calculate_challenge_streak(db, user_id, challenge.id)
        completed_today = (
            db.query(ChallengeCompletion)
            .filter(
                ChallengeCompletion.user_id == user_id,
                ChallengeCompletion.challenge_id == challenge.id,
                ChallengeCompletion.completion_date == today,
            )
            .first()
            is not None
        )
        results.append({
            "challenge_id": challenge.id,
            "title": challenge.title,
            "current_streak": current_streak,
            "completed_today": completed_today,
        })

    return results