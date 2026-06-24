from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from dependencies.database import Base


class Habit(Base):
    __tablename__ = "habits"
    __table_args__ = (UniqueConstraint("user_id", "slug", name="uq_habits_user_slug"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), nullable=False, index=True)
    category = Column(String(50), nullable=False, default="custom")
    unit = Column(String(20), nullable=False, default="count")
    track_method = Column(String(20), nullable=False, default="numeric")
    frequency = Column(String(30), nullable=False, default="daily")
    target_value = Column(Float, nullable=False, default=1.0)
    current_value = Column(Float, nullable=False, default=0.0)
    streak_count = Column(Integer, nullable=False, default=0)
    completed_today = Column(Boolean, nullable=False, default=False)
    last_completed_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
