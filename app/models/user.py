from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.mixins import TimestampMixin
from typing import Optional
from db.database import get_session
from sqlmodel import Field, Session, SQLModel, create_engine, select

class User(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

def get_user(user_id: int):
    with next(get_session()) as session:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()
    
def create_user(user: User):
    with next(get_session()) as session:
        session.add(user)
        session.commit()
        
def update_user(user: User):
    with next(get_session()) as session:
        statement = select(User).where(User.id == user.id)
        
