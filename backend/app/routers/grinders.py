from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Grinder
from app.models.user import User
from app.schemas import GrinderCreate, GrinderResponse

router = APIRouter(prefix="/grinders", tags=["grinders"])


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
