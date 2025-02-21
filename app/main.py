# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.db.database import create_db_and_tables
from app.api.main import api_router

# Import business modules
from app.business.resource_setup import setup_resources
from app.business.runner_management import launch_runners, shutdown_all_runners

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB and tables
    create_db_and_tables()

    resources = setup_resources()
    image_identifier = resources.db_image.identifier
    user_email = resources.system_user_email
    runner_count = resources.db_image.runner_pool_size
    await launch_runners(image_identifier, user_email, runner_count)

    # Yield so the app can start serving requests
    yield

    # On shutdown: terminate all launched instances
    await shutdown_all_runners()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello, welcome to the cloud ide dev backend!"}