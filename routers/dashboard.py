from fastapi import APIRouter

from controllers.dashboard_controller import get_dashboard
from controllers.workout_controller import list_workouts
from controllers.habit_controller import list_habits
from controllers.goal_controller import list_goals
from schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard_route():
    workouts = list_workouts()
    habits = list_habits()
    goals = list_goals()
    return get_dashboard(workouts, habits, goals)
