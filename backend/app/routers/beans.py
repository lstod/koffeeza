from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Bean
from app.models.shot import Shot
from app.models.user import User
from app.schemas import BeanCreate, BeanResponse

router = APIRouter(prefix="/beans", tags=["beans"])


def _get_owned(bean_id: int, db: Session, user: User) -> Bean:
    bean = db.get(Bean, bean_id)
    if not bean or bean.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bean not found")
    return bean


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


@router.put("/{bean_id}", response_model=BeanResponse)
def update_bean(
    bean_id: int,
    payload: BeanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bean = _get_owned(bean_id, db, current_user)
    for key, value in payload.model_dump().items():
        setattr(bean, key, value)
    db.commit()
    db.refresh(bean)
    return bean


@router.delete("/{bean_id}", status_code=status.HTTP_200_OK)
def delete_bean(
    bean_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bean = _get_owned(bean_id, db, current_user)
    deleted_shots = db.query(Shot).filter(Shot.bean_id == bean_id).delete()
    db.delete(bean)
    db.commit()
    return {"deleted_shots": deleted_shots}
