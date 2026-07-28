from datetime import datetime
from pydantic import BaseModel, Field


class MoodCreate(BaseModel):
    mood: str = Field(..., example="Good", description="Mood state or custom description")
    note: str | None = Field(None, example="Had a productive day!", description="Optional journal note")


class MoodUpdate(BaseModel):
    mood: str | None = Field(None, example="Great")
    note: str | None = Field(None, example="Updated note details")


class MoodResponse(BaseModel):
    id: int | None = Field(None, example=1, description="Optional unique identifier")
    timestamp: datetime = Field(..., example="2026-07-28 17:45:00")
    mood: str = Field(..., example="Good")
    note: str | None = Field(None, example="Had a productive day!")

    class Config:
        from_attributes = True


class MoodSummaryResponse(BaseModel):
    summary: dict[str, int] = Field(
        ..., 
        example={"Great": 5, "Good": 12, "Stressed": 2}
    )
    total_entries: int = Field(..., example=19)
