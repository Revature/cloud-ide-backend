import os
import json
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlmodel import Field, Session, SQLModel, create_engine, select
from app.models import machine, image, runner, role, user_role, script, runner_history
from app.models.user import User, UserUpdate, create_user, get_user, update_user, delete_user
from app.models.role import Role
from app.db.database import get_session, create_db_and_tables

# from app.api.main import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB and tables
    #create_db_and_tables()
    # start_scheduler()
    yield
    # Shutdown: Cleanup code (if needed)

load_dotenv()
app = FastAPI(lifespan=lifespan)
# app.include_router(api_router)

@app.get("/users/{id}")
def read_root(id: int):
    user = get_user(id)
    return user

@app.post("/users")
def post(user: User):
    return create_user(user)
    
@app.put("/users")
def put(userUpdate: UserUpdate):   
    return update_user(userUpdate)
 

@app.delete("/users/{id}")
def read_root(id: int):
    delete_user(id)


@app.delete("/resetdb")
def reset_db():
    create_db_and_tables()
    
