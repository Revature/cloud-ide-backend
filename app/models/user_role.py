from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped
from app.models.mixins import TimestampMixin

class UserRole(TimestampMixin, SQLModel, table=True):
    __tablename__ = "user_role"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

    # Relationships
    # user: Mapped["User"] = Relationship(back_populates="user_roles")
    # role: Mapped["Role"] = Relationship(back_populates="user_roles")