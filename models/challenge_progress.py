from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from dependencies.database import Base


class ChallengeProgress(Base):
    """Tracks cumulative progress toward a challenge (used for weekly/progress-based challenges)."""
    __tablename__ = "challenge_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, index=True)
    current_value = Column(Float, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge_progress"),
    )