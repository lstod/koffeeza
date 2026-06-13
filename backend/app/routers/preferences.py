from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.preference import Preference
from app.models.user import User
from app.schemas import PreferenceResponse, PreferenceUpdate

router = APIRouter(prefix="/preferences", tags=["preferences"])


def _get_or_create(db: Session, user: User) -> Preference:
    pref = db.query(Preference).filter(Preference.user_id == user.id).first()
    if pref is None:
        pref = Preference(user_id=user.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


@router.get("", response_model=PreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_or_create(db, current_user)


@router.put("", response_model=PreferenceResponse)
def update_preferences(
    payload: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = _get_or_create(db, current_user)
    if payload.grinder_id is not None:
        pref.grinder_id = payload.grinder_id
    if payload.machine_id is not None:
        pref.machine_id = payload.machine_id
    db.commit()
    db.refresh(pref)
    return pref
