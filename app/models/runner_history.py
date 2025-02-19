from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from app.models.mixins import TimestampMixin

class RunnerHistory(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    runner_id: int = Field(foreign_key="runner.id")
    event_name: str
    event_data: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON, nullable=False)
    )
    modified_by: str = Field(default="")
    created_by: str = Field(default="")