from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from app.models.mixins import TimestampMixin

class Role(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

    # Relationship
    # user_roles: Mapped[List["UserRole"]] = Relationship(back_populates="role")