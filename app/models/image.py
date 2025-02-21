from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin
from app.db import database

class Image(TimestampMixin, SQLModel, table=True):
    # id: Optional[int] = Field(default=None, primary_key=True)
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    identifier: str
    modified_by: str | None = Field(default="")
    created_by: str | None = Field(default="")

class ImageUpdate(TimestampMixin, SQLModel):
    id: int
    name: str | None = None
    description: str | None = None
    identifier: str | None = None
    
def create_image(image: Image):
    with next(database.get_session()) as session:
        session.add(image)
        session.refresh()
    return image

def update_image(image: ImageUpdate):
    with next(database.get_session()) as session:
        image_from_db = session.get(Image, image.id)
        image_data = image.model_dump(exclude_unset=True)
        image_from_db.sqlmodel_update(image_data)
        session.add(image_from_db)
        session.commit()
        session.refresh(image_from_db)
        return image_from_db


def get_image(image_id: int):
    with next(database.get_session()) as session:
        return session.get(Image, image_id)

def delete_image(image_id: int):
    with next(database.get_session()) as session:
        session.delete(image_id)