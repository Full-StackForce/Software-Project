from typing import List

from schemas.dashboard import DashboardResponse
from models.workout import Workout
from models.habit import Habit
from models.goal import Goal


def get_dashboard(workouts: List[Workout], habits: List[Habit], goals: List[Goal]) -> DashboardResponse:
    active_habits = sum(1 for habit in habits if habit.completed_today or habit.streak_count > 0)
    goals_completed = sum(1 for goal in goals if goal.completed)
    streak_summary = f"{sum(habit.streak_count for habit in habits)} total streak days"

    return DashboardResponse(
        total_workouts=len(workouts),
        active_habits=active_habits,
        goals_completed=goals_completed,
        streak_summary=streak_summary,
    )
