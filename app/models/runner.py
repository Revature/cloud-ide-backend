from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from sqlalchemy.orm import Mapped
from app.models.mixins import TimestampMixin
from app.db import database

# states
# runner_starting
# app_starting
# ready
# setup
# awaiting_client
# active
# disconnecting
# disconnected
# closed
# terminated

# runner_alive states = [runner_starting, app_starting, ready, setup, awaiting_client, active, disconnecting, disconnected]
# runner_dead states = [closed, terminated]

# Relationships
# machine: Mapped["Machine"] = Relationship(back_populates="runners")
# image: Mapped["Image"] = Relationship(back_populates="runners")
# user: Mapped["User"] = Relationship(back_populates="runners")
# runner_histories: Mapped[List["RunnerHistory"]] = Relationship(back_populates="runner")

class Runner(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key="machine.id")
    image_id: int = Field(foreign_key="image.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    key_id: Optional[int] = Field(default=None, foreign_key="keys.id")
    state: str
    url: str
    token: str
    identifier: str
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
    
    @property
    def is_alive_state(self) -> bool:
        """Returns True if the runner's state is considered 'alive'."""
        alive_states = {
            "runner_starting", "app_starting", "ready", "setup",
            "awaiting_client", "active", "disconnecting", "disconnected"
        }
        return self.state in alive_states

    
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