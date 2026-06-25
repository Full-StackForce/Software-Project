from datetime import date, datetime

from pydantic import BaseModel, Field


class WeightLogCreate(BaseModel):
    weight_kg: float = Field(..., gt=0, example=68.5)
    log_date: date | None = Field(None, example="2026-06-24")


class WeightLogResponse(BaseModel):
    id: int
    user_id: int
    log_date: date
    weight_kg: float
    created_at: datetime

    class Config:
        from_attributes = True