from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.machine import Machine

router = APIRouter()

@router.post("/", response_model=Machine, status_code=status.HTTP_201_CREATED)
def create_machine(machine: Machine, session: Session = Depends(get_session)):
    """
    Create a new Machine record.
    """
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine
  
@router.get("/", response_model=List[Machine])
def read_machines(session: Session = Depends(get_session)):
    """
    Retrieve a list of all Machines.
    """
    machines = session.exec(select(Machine)).all()
    return machines

@router.get("/{machine_id}", response_model=Machine)
def read_machine(machine_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single Machine by ID.
    """
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
  
@route.patch("/{machine_id}", response_model=Machine)
def update_machine(machine_id: int, updated_machine: Machine, session: Session = Depends(get_session)):
    """
    Update an existing Machine record.
    """
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Update fields; typically, you might want to limit which fields can be updated.
    machine.name = updated_machine.name
    machine.description = updated_machine.description
    machine.identifier = updated_machine.identifier
    machine.modified_by = updated_machine.modified_by
    
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine