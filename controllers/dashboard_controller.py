from typing import List

from schemas.dashboard import DashboardResponse
from models.workout import Workout
from models.habit import Habit
from models.goal import Goal


def _habit_progress_pct(habits: List[Habit], slug: str) -> int:
    habit = next((item for item in habits if getattr(item, "slug", "") == slug), None)
    if not habit:
        return 0

    target = max(float(getattr(habit, "target_value", 0) or 0), 0.0001)
    value = max(float(getattr(habit, "current_value", 0) or 0), 0)
    return min(100, int(round((value / target) * 100)))


def get_dashboard(workouts: List[Workout], habits: List[Habit], goals: List[Goal], current_streak_days: int) -> DashboardResponse:
    active_habits = sum(1 for habit in habits if habit.completed_today or habit.streak_count > 0)
    goals_completed = sum(1 for goal in goals if goal.completed)

    hydration_progress_pct = _habit_progress_pct(habits, "hydration")
    sleep_progress_pct = _habit_progress_pct(habits, "sleep")
    workout_progress_pct = _habit_progress_pct(habits, "workout")

    day_label = "day" if current_streak_days == 1 else "days"
    streak_summary = f"{current_streak_days} login {day_label} in a row"

    return DashboardResponse(
        total_workouts=len(workouts),
        active_habits=active_habits,
        goals_completed=goals_completed,
        current_streak_days=current_streak_days,
        streak_summary=streak_summary,
        hydration_progress_pct=hydration_progress_pct,
        sleep_progress_pct=sleep_progress_pct,
        workout_progress_pct=workout_progress_pct,
    )
