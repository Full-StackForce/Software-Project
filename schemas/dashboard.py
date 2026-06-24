from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_workouts: int
    active_habits: int
    goals_completed: int
    current_streak_days: int
    streak_summary: str
    hydration_progress_pct: int
    sleep_progress_pct: int
    workout_progress_pct: int
