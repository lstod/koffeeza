from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Bean, Grinder, Machine
from app.models.user import User
from app.recall.core import recall
from app.schemas import RecallResponse

router = APIRouter(prefix="/recall", tags=["recall"])


@router.get("", response_model=RecallResponse)
def get_recall(
    bean_id: int,
    grinder_id: int,
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bean = db.get(Bean, bean_id)
    if not bean or bean.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Bean {bean_id} not found")
    grinder = db.get(Grinder, grinder_id)
    if not grinder or grinder.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Grinder {grinder_id} not found")
    machine = db.get(Machine, machine_id)
    if not machine or machine.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Machine {machine_id} not found")

    result = recall(db, bean_id, grinder_id, machine_id, current_user.id)
    return RecallResponse(
        confidence_label=result.confidence_label,
        source_tier=result.source_tier,
        grind_setting_native=result.grind_setting_native,
        dose_g=result.dose_g,
        yield_g=result.yield_g,
        time_s=result.time_s,
        shot_id=result.shot_id,
    )
