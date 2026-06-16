from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_workouts: int
    active_habits: int
    goals_completed: int
    streak_summary: str
