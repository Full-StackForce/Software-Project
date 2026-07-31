from datetime import date
from typing import List

from sqlalchemy.orm import Session

from dependencies.database import SessionLocal
from models.user import User
from models.weight_log import WeightLog
from schemas.weight_log import WeightLogCreate


def create_weight_log(user_id: int, payload: WeightLogCreate) -> WeightLog | None:
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        log_entry = WeightLog(
            user_id=user_id,
            log_date=payload.log_date or date.today(),
            weight_lbs=payload.weight_lbs,
        )
        db.add(log_entry)

        # Keep profile weight aligned with latest explicit log.
        user.weight_lbs = payload.weight_lbs

        db.commit()
        db.refresh(log_entry)
        return log_entry
    finally:
        db.close()


def list_weight_logs_by_user(user_id: int) -> List[WeightLog] | None:
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        return (
            db.query(WeightLog)
            .filter(WeightLog.user_id == user_id)
            .order_by(WeightLog.log_date.asc(), WeightLog.id.asc())
            .all()
        )
    finally:
        db.close()