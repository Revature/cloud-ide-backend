from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin
from app.db.database import get_session
from app.models import user, role

class UserRole(TimestampMixin, SQLModel, table=True):
    __tablename__ = "user_role"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    role_id: int = Field(foreign_key="role.id")
    modified_by: str = Field(default="")
    created_by: str = Field(default="")
    

        
def assign_role(user: user.User, role_id: int):
    user_role: UserRole = UserRole(user_id = user.id, role_id = role_id)
    with next(get_session()) as session:
        session.add(user_role)
        session.commit()

def remove_role(role_id: int):
    with next(get_session()) as session:
        session.delete(role_id)
        
