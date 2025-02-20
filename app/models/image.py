from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from app.models.mixins import TimestampMixin

class Image(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    identifier: str
    runner_pool_size: int = Field(default=1)
    machine_id: Optional[int] = Field(default=None, foreign_key="machine.id")
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

    # Relationships
    # machine: Mapped[Optional["Machine"]] = Relationship(back_populates="images")
    # runners: Mapped[List["Runner"]] = Relationship(back_populates="image")
    # scripts: Mapped[List["Script"]] = Relationship(back_populates="image")