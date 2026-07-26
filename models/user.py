from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from dependencies.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    timezone = Column(String(100), nullable=True)
    focus = Column(String(255), nullable=True)
    gender = Column(String(30), nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    target_weight_kg = Column(Float, nullable=True)
    bedtime = Column(String(20), nullable=True)
    active_days = Column(Integer, nullable=True)
    hydration_goal = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
