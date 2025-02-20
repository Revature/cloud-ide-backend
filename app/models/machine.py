from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.mixins import TimestampMixin

class Machine(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    identifier: str
    cpu_count: int
    memory_size: int
    storage_size: int
    modified_by: str = Field(default="")
    created_by: str = Field(default="")