# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.db.database import create_db_and_tables, engine
from app.api.main import api_router
import uuid

# Import your models
from app.models.image import Image
from app.models.machine import Machine
from app.models.runner import Runner
from app.models.user import User

# Import your AWS functions
from app.business.aws import Create_New_EC2, Describe_EC2, Stop_EC2, Terminate_EC2

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) Create DB and tables
    create_db_and_tables()

    # Keep track of the instance IDs so we can stop them on shutdown
    launched_instance_ids = []

    with Session(engine) as session:
        
        stmt_user = select(User).where(User.email == "ashoka.shringla@revature.com")
        system_user = session.exec(stmt_user).first()
        if not system_user:
            system_user = User(
                first_name="Ashoka",
                last_name="Shringla",
                email="ashoka.shringla@revature.com",
                created_by="system",
                modified_by="system"
            )
            session.add(system_user)
            session.commit()
            session.refresh(system_user)
        
        # -- Create (or fetch) default Image --
        stmt_image = select(Image).where(Image.identifier == "ami-07f9ff58e9ab20148")
        db_image = session.exec(stmt_image).first()
        if not db_image:
            db_image = Image(
                name="sample-id-image",
                description="An AMI for testing",
                identifier="ami-07f9ff58e9ab20148",
                runner_pool_size=2,  # Example pool size
                created_by="system",
                modified_by="system"
            )
            session.add(db_image)
            session.commit()
            session.refresh(db_image)

        # -- Create (or fetch) default Machine --
        stmt_machine = select(Machine).where(Machine.identifier == "default-machine")
        db_machine = session.exec(stmt_machine).first()
        if not db_machine:
            db_machine = Machine(
                name="t2.medium",
                identifier="t2.medium",
                cpu_count=2,
                memory_size=4096,
                storage_size=20,
                created_by="system",
                modified_by="system"
            )
            session.add(db_machine)
            session.commit()
            session.refresh(db_machine)
            
        # add machine to image
        db_image.machine_id = db_machine.id
        session.commit()

        # 2) Launch multiple EC2 instances based on runner_pool_size
        for _ in range(db_image.runner_pool_size):
            instance_id = await Create_New_EC2(
                ImageId=db_image.identifier,  # e.g. "ami-0f9f85e9aeb20148"
                InstanceType = db_image.machine.identifier if db_image.machine else "t2.medium",
                InstanceCount=1
            )
            launched_instance_ids.append(instance_id)

            # 3) Retrieve the public IP
            public_ip = await Describe_EC2(instance_id)

            # 4) Create a Runner record
            new_runner = Runner(
                machine_id=db_machine.id,
                image_id=db_image.id,
                user_id=system_user.id,
                state="ready",
                url=public_ip or "",
                token="",
                identifier=instance_id,
                external_hash=uuid.uuid4().hex,
                session_start=datetime.utcnow(),
                session_end=datetime.now() + timedelta(minutes=30),
                created_by="system",
                modified_by="system"
            )
            session.add(new_runner)
            session.commit()

    # Yield here so the app can start serving requests
    yield

    # -- On shutdown: Stop all the instances we launched --
    for instance_id in launched_instance_ids:
        await Stop_EC2(instance_id)
        await Terminate_EC2(instance_id)

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello, welcome to the cloud ide dev backend!"}