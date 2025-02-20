from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from app.models.mixins import TimestampMixin

class Runner(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key="machine.id")
    image_id: int = Field(foreign_key="image.id")
    user_id: int = Field(foreign_key="user.id")
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

    # Relationships
    machine: "Machine" = Relationship(back_populates="runners")
    image: "Image" = Relationship(back_populates="runners")
    user: "User" = Relationship(back_populates="runners")
    runner_histories: List["RunnerHistory"] = Relationship(back_populates="runner")
    