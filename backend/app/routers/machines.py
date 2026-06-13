from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Machine
from app.models.shot import Shot
from app.models.user import User
from app.schemas import MachineCreate, MachineResponse

router = APIRouter(prefix="/machines", tags=["machines"])


def _get_owned(machine_id: int, db: Session, user: User) -> Machine:
    machine = db.get(Machine, machine_id)
    if not machine or machine.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Machine not found")
    return machine


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


@router.put("/{machine_id}", response_model=MachineResponse)
def update_machine(
    machine_id: int,
    payload: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    machine = _get_owned(machine_id, db, current_user)
    for key, value in payload.model_dump().items():
        setattr(machine, key, value)
    db.commit()
    db.refresh(machine)
    return machine


@router.delete("/{machine_id}", status_code=status.HTTP_200_OK)
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    machine = _get_owned(machine_id, db, current_user)
    deleted_shots = db.query(Shot).filter(Shot.machine_id == machine_id).delete()
    db.delete(machine)
    db.commit()
    return {"deleted_shots": deleted_shots}
