# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.db.database import create_db_and_tables
from app.api.main import api_router
# from app.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create DB and tables
    create_db_and_tables()
    # start_scheduler()
    yield
    # Shutdown: Cleanup code (if needed)

load_dotenv()
app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello, welcome to the cloud ide dev backend!"}