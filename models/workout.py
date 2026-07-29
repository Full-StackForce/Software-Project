from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.sql import func

from dependencies.database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(80), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Integer, nullable=False, default=0)
    notes = Column(String(500), nullable=True)
    mood = Column(String(60), nullable=True)
    mood_level = Column(Integer, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

