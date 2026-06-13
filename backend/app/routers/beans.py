from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Bean
from app.models.user import User
from app.schemas import BeanCreate, BeanResponse

router = APIRouter(prefix="/beans", tags=["beans"])


@router.get("", response_model=list[BeanResponse])
def list_beans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Bean).filter(Bean.user_id == current_user.id).all()


@router.post("", response_model=BeanResponse, status_code=status.HTTP_201_CREATED)
def create_bean(
    payload: BeanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bean = Bean(**payload.model_dump(), user_id=current_user.id)
    db.add(bean)
    db.commit()
    db.refresh(bean)
    return bean
