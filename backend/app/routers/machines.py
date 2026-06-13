from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Machine
from app.models.user import User
from app.schemas import MachineCreate, MachineResponse

router = APIRouter(prefix="/machines", tags=["machines"])


@router.get("", response_model=list[MachineResponse])
def list_machines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Machine).filter(Machine.user_id == current_user.id).all()


@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(
    payload: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    machine = Machine(**payload.model_dump(), user_id=current_user.id)
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine
