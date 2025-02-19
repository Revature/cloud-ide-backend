from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin

class Runner(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key="machine.id")
    image_id: int = Field(foreign_key="image.id")
    user_id: int = Field(foreign_key="user.id")
    state: str
    pool_status: str
    url: str
    started_on: datetime
    ended_on: Optional[datetime] = None
    modified_by: str = Field(default="")
    created_by: str = Field(default="")