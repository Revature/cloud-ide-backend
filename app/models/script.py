from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin

class Script(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    event: str
    image_id: int = Field(foreign_key="image.id")
    script: str
    modified_by: str = Field(default="")
    created_by: str = Field(default="")