# app/models/mixins.py
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import Column, DateTime

class TimestampMixin(SQLModel):
    created_on: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Database timestamp when the record was created.",
    )
    updated_on: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )