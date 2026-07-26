from fastapi import APIRouter, HTTPException

from controllers.weight_log_controller import create_weight_log, list_weight_logs_by_user
from schemas.weight_log import WeightLogCreate, WeightLogResponse

router = APIRouter(prefix="/users", tags=["weight-logs"])


@router.get("/{user_id}/weight-logs", response_model=list[WeightLogResponse])
def get_weight_logs_route(user_id: int):
    logs = list_weight_logs_by_user(user_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="User not found")
    return logs


@router.post("/{user_id}/weight-logs", response_model=WeightLogResponse)
def create_weight_log_route(user_id: int, payload: WeightLogCreate):
    log_entry = create_weight_log(user_id, payload)
    if not log_entry:
        raise HTTPException(status_code=404, detail="User not found")
    return log_entry