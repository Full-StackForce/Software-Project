from datetime import date, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.challenge import Challenge
from models.challenge_completion import ChallengeCompletion
from models.user import User
from models.challenge_progress import ChallengeProgress


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
def get_user_stats(db: Session, user_id: int) -> dict:
    today = date.today()

    completions = db.query(ChallengeCompletion).filter(ChallengeCompletion.user_id == user_id).all()
    completed_count = len(completions)

    total_xp = 0
    for completion in completions:
        challenge = db.query(Challenge).filter(Challenge.id == completion.challenge_id).first()
        if challenge:
            total_xp += challenge.xp_reward

    all_daily_challenges = db.query(Challenge).filter(Challenge.challenge_type == "daily").all()
    completed_today_ids = {
        c.challenge_id
        for c in db.query(ChallengeCompletion)
        .filter(ChallengeCompletion.user_id == user_id, ChallengeCompletion.completion_date == today)
        .all()
    }
    active_challenges = len([c for c in all_daily_challenges if c.id not in completed_today_ids])

    return {
        "current_xp": total_xp,
        "completed_count": completed_count,
        "active_challenges": active_challenges,
    }


def get_weekly_challenges(db: Session, user_id: int) -> List[dict]:
    weekly_challenges = db.query(Challenge).filter(Challenge.challenge_type == "weekly").all()
    results = []

    for challenge in weekly_challenges:
        progress = (
            db.query(ChallengeProgress)
            .filter(ChallengeProgress.user_id == user_id, ChallengeProgress.challenge_id == challenge.id)
            .first()
        )
        current_value = progress.current_value if progress else 0
        target_value = challenge.target_value or 1
        percent_complete = min(100, round((current_value / target_value) * 100, 1))

        results.append({
            "challenge_id": challenge.id,
            "title": challenge.title,
            "description": challenge.description,
            "target_value": target_value,
            "current_value": current_value,
            "percent_complete": percent_complete,
            "unit": challenge.unit,
        })

    return results


def update_weekly_progress(db: Session, user_id: int, challenge_id: int, increment: float) -> dict:
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.challenge_type == "weekly").first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Weekly challenge not found")

    progress = (
        db.query(ChallengeProgress)
        .filter(ChallengeProgress.user_id == user_id, ChallengeProgress.challenge_id == challenge_id)
        .first()
    )

    if not progress:
        progress = ChallengeProgress(user_id=user_id, challenge_id=challenge_id, current_value=0)
        db.add(progress)

    progress.current_value = min((challenge.target_value or 0), progress.current_value + increment)
    db.commit()

    target_value = challenge.target_value or 1
    percent_complete = min(100, round((progress.current_value / target_value) * 100, 1))

    return {
        "challenge_id": challenge_id,
        "title": challenge.title,
        "description": challenge.description,
        "target_value": target_value,
        "current_value": progress.current_value,
        "percent_complete": percent_complete,
        "unit": challenge.unit,
    }