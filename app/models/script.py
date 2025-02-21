from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.mixins import TimestampMixin
from app.db import database

class Script(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    event: str
    image_id: int = Field(foreign_key="image.id")
    script: str
    modified_by: str = Field(default="")
    created_by: str = Field(default="")

class ScriptUpdate(TimestampMixin, SQLModel):
    id: int
    name: str | None = None
    description: str | None = None
    event: str | None = None
    script: str | None = None
    
    
def create_script(script: Script):
    with next(database.get_session()) as session:
        session.add(script)
        session.refresh()
    return script

def update_script(script: ScriptUpdate):
    with next(database.get_session()) as session:
        script_from_db = session.get(Script, script.id)
        script_data = script.model_dump(exclude_unset=True)
        script_from_db.sqlmodel_update(script_data)
        session.add(script_from_db)
        session.commit()
        session.refresh(script_from_db)
        return script_from_db


def get_script(script_id: int):
    with next(database.get_session()) as session:
        return session.get(Script, script_id)

def delete_script(script_id: int):
    with next(database.get_session()) as session:
        session.delete(script_id)
        #session.commit() #this is implicitly called when the session goes out?