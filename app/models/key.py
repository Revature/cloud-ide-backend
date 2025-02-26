from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, TEXT
from sqlalchemy import UniqueConstraint
from app.models.mixins import TimestampMixin

class Key(TimestampMixin, SQLModel, table=True):
    __table_args__ = (UniqueConstraint("key_date"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    key_date: date = Field(nullable=False, index=True)
    key_pair_id: str = Field(nullable=False)
    key_name: str = Field(nullable=False)
    encrypted_key: str = Field(sa_column=Column(TEXT, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)