from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Machine
from app.schemas import MachineCreate, MachineResponse

router = APIRouter(prefix="/machines", tags=["machines"])


@router.get("", response_model=list[MachineResponse])
def list_machines(db: Session = Depends(get_db)):
    return db.query(Machine).all()


@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
def create_machine(payload: MachineCreate, db: Session = Depends(get_db)):
    machine = Machine(**payload.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine
