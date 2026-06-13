from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Grinder
from app.schemas import GrinderCreate, GrinderResponse

router = APIRouter(prefix="/grinders", tags=["grinders"])


@router.get("", response_model=list[GrinderResponse])
def list_grinders(db: Session = Depends(get_db)):
    return db.query(Grinder).all()


@router.post("", response_model=GrinderResponse, status_code=status.HTTP_201_CREATED)
def create_grinder(payload: GrinderCreate, db: Session = Depends(get_db)):
    grinder = Grinder(**payload.model_dump())
    db.add(grinder)
    db.commit()
    db.refresh(grinder)
    return grinder
