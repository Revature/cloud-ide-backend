from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from app.models.mixins import TimestampMixin

class Machine(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    identifier: str
    cpu_count: int
    memory_size: int
    storage_size: int
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

    # Relationships
    # images: Mapped[List["Image"]] = Relationship(back_populates="machine")
    # runners: Mapped[List["Runner"]] = Relationship(back_populates="machine")