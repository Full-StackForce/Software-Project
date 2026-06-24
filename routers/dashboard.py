from datetime import date, timedelta

from fastapi import APIRouter
from sqlalchemy.orm import Session

from controllers.dashboard_controller import get_dashboard
from controllers.workout_controller import list_workouts, list_workouts_by_user
from controllers.habit_controller import list_habits, list_habits_by_user
from controllers.goal_controller import list_goals, list_goals_by_user
from dependencies.database import SessionLocal
from models.login_activity import LoginActivity
from schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _calculate_login_streak(user_id: int) -> int:
    db: Session = SessionLocal()
    try:
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
    finally:
        db.close()


@router.get("/", response_model=DashboardResponse)
def get_dashboard_route():
    workouts = list_workouts()
    habits = list_habits()
    goals = list_goals()
    return get_dashboard(workouts, habits, goals, current_streak_days=0)


@router.get("/user/{user_id}", response_model=DashboardResponse)
def get_user_dashboard(user_id: int):
    workouts = list_workouts_by_user(user_id)
    habits = list_habits_by_user(user_id)
    goals = list_goals_by_user(user_id)
    current_streak_days = _calculate_login_streak(user_id)
    return get_dashboard(workouts, habits, goals, current_streak_days=current_streak_days)
