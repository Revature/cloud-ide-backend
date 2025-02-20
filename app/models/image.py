from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from models.mixins import TimestampMixin

class Image(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    identifier: str
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

