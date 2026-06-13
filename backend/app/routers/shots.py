from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapter import to_instruction
from app.database import get_db
from app.engine import ShotInput, recommend
from app.models import Bean, Grinder, Machine, Shot
from app.models.preference import Preference
from app.rationale import render_rationale
from app.schemas import ShotCreate, ShotResponse, ShotSuggestionResponse

router = APIRouter(prefix="/shots", tags=["shots"])


@router.get("", response_model=list[ShotResponse])
def list_shots(bean_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Shot).order_by(Shot.created_at.desc(), Shot.id.desc())
    if bean_id is not None:
        query = query.filter(Shot.bean_id == bean_id)
    return query.all()


@router.post(
    "",
    response_model=ShotSuggestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shot(payload: ShotCreate, db: Session = Depends(get_db)):
    bean = db.get(Bean, payload.bean_id)
    if not bean:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Bean {payload.bean_id} not found")

    grinder = db.get(Grinder, payload.grinder_id)
    if not grinder:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Grinder {payload.grinder_id} not found")

    machine = db.get(Machine, payload.machine_id)
    if not machine:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Machine {payload.machine_id} not found")

    try:
        current_native = float(payload.grind_setting_native)
    except ValueError:
        current_native = None

    shot_input = ShotInput(
        dose_g=payload.dose_g,
        yield_g=payload.yield_g,
        time_s=payload.time_s,
        taste=payload.taste,
        intensity=payload.intensity,
        roast_date=payload.roast_date,
    )

    decision = recommend(shot_input)
    instruction = to_instruction(
        grinder, current_native, decision.direction, decision.magnitude_normalized
    )
    rationale = render_rationale(decision.reason_code, decision.facts)

    shot = Shot(
        **payload.model_dump(),
        reason_code=decision.reason_code,
    )
    db.add(shot)
    db.flush()

    pref = db.get(Preference, 1)
    if pref is None:
        pref = Preference(id=1, grinder_id=payload.grinder_id, machine_id=payload.machine_id)
        db.add(pref)
    else:
        pref.grinder_id = payload.grinder_id
        pref.machine_id = payload.machine_id

    db.commit()
    db.refresh(shot)

    return ShotSuggestionResponse(
        shot=ShotResponse.model_validate(shot),
        direction=decision.direction.value if decision.direction.value != "NONE" else None,
        magnitude_normalized=decision.magnitude_normalized,
        confidence=decision.confidence.value,
        instruction=instruction.text,
        rationale=rationale,
    )
