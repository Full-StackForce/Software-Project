from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from dependencies.database import Base


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(50), nullable=True)  # e.g. "hydration", "sleep", "workout", "steps"
    icon = Column(String(10), nullable=True)  # emoji, matches frontend
    xp_reward = Column(Integer, nullable=False, default=10)
    target_value = Column(Float, nullable=True)  # e.g. 2.5 (liters), 10000 (steps)
    unit = Column(String(20), nullable=True)  # e.g. "liters", "steps", "hours"
    challenge_type = Column(String(20), nullable=False, default="daily")  # "daily" or "weekly"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)