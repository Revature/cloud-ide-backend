from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.mixins import TimestampMixin

class User(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

    # Relationships
    runners: List["Runner"] = Relationship(back_populates="user")
    user_roles: List["UserRole"] = Relationship(back_populates="user")