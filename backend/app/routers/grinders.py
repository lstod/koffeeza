from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Grinder
from app.models.shot import Shot
from app.models.user import User
from app.schemas import GrinderCreate, GrinderResponse

router = APIRouter(prefix="/grinders", tags=["grinders"])


def _get_owned(grinder_id: int, db: Session, user: User) -> Grinder:
    grinder = db.get(Grinder, grinder_id)
    if not grinder or grinder.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Grinder not found")
    return grinder


@router.get("", response_model=list[GrinderResponse])
def list_grinders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Grinder).filter(Grinder.user_id == current_user.id).all()


@router.post("", response_model=GrinderResponse, status_code=status.HTTP_201_CREATED)
def create_grinder(
    payload: GrinderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grinder = Grinder(**payload.model_dump(), user_id=current_user.id)
    db.add(grinder)
    db.commit()
    db.refresh(grinder)
    return grinder


@router.put("/{grinder_id}", response_model=GrinderResponse)
def update_grinder(
    grinder_id: int,
    payload: GrinderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grinder = _get_owned(grinder_id, db, current_user)
    for key, value in payload.model_dump().items():
        setattr(grinder, key, value)
    db.commit()
    db.refresh(grinder)
    return grinder


@router.delete("/{grinder_id}", status_code=status.HTTP_200_OK)
def delete_grinder(
    grinder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grinder = _get_owned(grinder_id, db, current_user)
    deleted_shots = db.query(Shot).filter(Shot.grinder_id == grinder_id).delete()
    db.delete(grinder)
    db.commit()
    return {"deleted_shots": deleted_shots}
