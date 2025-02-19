from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Machine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    identifier: str
    modified_on: datetime = Field(default_factory=datetime.utcnow)
    modified_by: str = Field(default="")
    created_on: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="")