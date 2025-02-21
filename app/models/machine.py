from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin
from app.db import database

class Machine(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    identifier: str
    cpu_count: int
    memory_size: int
    storage_size: int
    modified_by: str = Field(default="")
    created_by: str = Field(default="")
    
class MachineUpdate(TimestampMixin, SQLModel):
    id: int
    name: str | None = None
    identifier: str | None = None
    cpu_count: int | None = None
    memory_size: int | None = None
    storage_size: int | None = None

def create_machine(machine: Machine):
    with next(database.get_session()) as session:
        session.add(machine)
        session.refresh()
    return machine

def update_machine(machine: MachineUpdate):
    with next(database.get_session()) as session:
        machine_from_db = session.get(Machine, machine.id)
        machine_data = machine.model_dump(exclude_unset=True)
        machine_from_db.sqlmodel_update(machine_data)
        session.add(machine_from_db)
        session.commit()
        session.refresh(machine_from_db)
        return machine_from_db


def get_machine(machine_id: int):
    with next(database.get_session()) as session:
        return session.get(Machine, machine_id)

def delete_machine(machine_id: int):
    with next(database.get_session()) as session:
        session.delete(machine_id)
        #session.commit() #this is implicitly called when the session goes out?