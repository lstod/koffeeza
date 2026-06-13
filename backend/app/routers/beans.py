from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bean
from app.schemas import BeanCreate, BeanResponse

router = APIRouter(prefix="/beans", tags=["beans"])


@router.get("", response_model=list[BeanResponse])
def list_beans(db: Session = Depends(get_db)):
    return db.query(Bean).all()


@router.post("", response_model=BeanResponse, status_code=status.HTTP_201_CREATED)
def create_bean(payload: BeanCreate, db: Session = Depends(get_db)):
    bean = Bean(**payload.model_dump())
    db.add(bean)
    db.commit()
    db.refresh(bean)
    return bean
