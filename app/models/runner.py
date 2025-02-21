from typing import Optional, Dict, Any
from sqlalchemy import Column, JSON
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin
from app.db import database

class Runner(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key="machine.id")
    image_id: int = Field(foreign_key="image.id")
    user_id: int = Field(foreign_key="user.id")
    state: str
    url: str
    token: str
    external_hash: str
    env_data: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON, nullable=False)
    )
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    ended_on: Optional[datetime] = None
    modified_by: str = Field(default="")
    created_by: str = Field(default="")
    
class RunnerUpdate(TimestampMixin, SQLModel):
    id: int
    state: str
    url: str
    token: str
    external_hash: str
    env_data: Dict[str, Any] | None = None
    session_start: datetime | None = None
    session_end: datetime | None = None
    ended_on: datetime | None = None
    
def create_runner(runner: Runner):
    with next(database.get_session()) as session:
        session.add(runner)
        session.refresh()
    return runner

def update_runner(runner: RunnerUpdate):
    with next(database.get_session()) as session:
        runner_from_db = session.get(Runner, runner.id)
        runner_data = runner.model_dump(exclude_unset=True)
        runner_from_db.sqlmodel_update(runner_data)
        session.add(runner_from_db)
        session.commit()
        session.refresh(runner_from_db)
        return runner_from_db


def get_runner(runner_id: int):
    with next(database.get_session()) as session:
        return session.get(Runner, runner_id)

def delete_runner(runner_id: int):
    with next(database.get_session()) as session:
        session.delete(runner_id)
        #session.commit() #this is implicitly called when the session goes out?