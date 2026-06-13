from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_token, hash_pin, verify_pin
from app.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserLogin, UserLoginResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.name).all()


@router.post("", response_model=UserLoginResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.name == payload.name).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "A user with this name already exists")

    user = User(
        name=payload.name,
        pin_hash=hash_pin(payload.pin) if payload.pin else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserLoginResponse(
        user=UserResponse.model_validate(user),
        token=create_token(user.id),
    )


@router.post("/{user_id}/login", response_model=UserLoginResponse)
def login(user_id: int, payload: UserLogin, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if user.pin_hash is not None:
        if not payload.pin:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "PIN required")
        if not verify_pin(payload.pin, user.pin_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect PIN")

    return UserLoginResponse(
        user=UserResponse.model_validate(user),
        token=create_token(user.id),
    )
