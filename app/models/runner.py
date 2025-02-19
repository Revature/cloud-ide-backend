from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Runner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    machine_id: int = Field(foreign_key="machine.id")
    image_id: int = Field(foreign_key="image.id")
    user_id: int = Field(foreign_key="user.id")
    state: str
    pool_status: str
    url: str
    started_on: datetime
    ended_on: Optional[datetime] = None
    modified_on: datetime = Field(default_factory=datetime.utcnow)
    modified_by: str = Field(default="")
    created_on: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="")