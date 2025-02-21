from typing import Optional
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin
from app.db.database import get_session

# class RoleEnum(Enum):
#     ADMIN = "admin",
#     USER = "user",
#     REPORTER = "reporter"

class Role(TimestampMixin, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    modified_by: None | str = Field(default="")
    created_by: None | str = Field(default="")

    
def populate_roles():
    role_admin: Role = Role(id = 1, name = "admin")
    role_user: Role = Role(id = 2, name = "user")
    with next(get_session()) as session:
        session.add(role_admin)
        session.add(role_user)
        session.commit()

