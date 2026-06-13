from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.preference import Preference
from app.schemas import PreferenceResponse, PreferenceUpdate

router = APIRouter(prefix="/preferences", tags=["preferences"])

_SINGLETON_ID = 1


def _get_or_create(db: Session) -> Preference:
    pref = db.get(Preference, _SINGLETON_ID)
    if pref is None:
        pref = Preference(id=_SINGLETON_ID)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.get("", response_model=PreferenceResponse)
def get_preferences(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.put("", response_model=PreferenceResponse)
def update_preferences(payload: PreferenceUpdate, db: Session = Depends(get_db)):
    pref = _get_or_create(db)
    if payload.grinder_id is not None:
        pref.grinder_id = payload.grinder_id
    if payload.machine_id is not None:
        pref.machine_id = payload.machine_id
    db.commit()
    db.refresh(pref)
    return pref
