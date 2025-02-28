# business/runner_management.py
import uuid
import asyncio
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.db.database import engine
from app.models import Machine, Image, Runner
from app.business.aws import Create_New_EC2, Stop_EC2, Terminate_EC2, wait_for_instance_running
from app.tasks.starting_runner import update_runner_state
from app.business.key_management import get_daily_key

async def launch_runners(image_identifier: str, runner_count: int):
    """
    Launches EC2 instances concurrently and creates Runner records after
    waiting for all instances to be running.
    Each new runner is associated with today's key.
    Returns a list of launched instance IDs.
    """
    launched_instance_ids = []
    
    # Open one DB session for reading resources.
    with Session(engine) as session:
        # 1) Fetch the Image.
        stmt_image = select(Image).where(Image.identifier == image_identifier)
        db_image = session.exec(stmt_image).first()
        if not db_image:
            raise Exception("Image not found")
        
        # 2) Fetch the Machine associated with the image.
        if db_image.machine_id is None:
            raise Exception("No machine associated with the image")
        stmt_machine = select(Machine).where(Machine.id == db_image.machine_id)
        db_machine = session.exec(stmt_machine).first()
        if not db_machine:
            raise Exception("Machine not found")
    
    # 3) Get or create today's key.
    key_record = await get_daily_key()  # Returns a Key model instance.
    if key_record is None:
        raise Exception("Key not found or created")
    
    # 4) Launch all EC2 instances concurrently.
    launch_tasks = [
        Create_New_EC2(
            ImageId=db_image.identifier,
            InstanceType=db_machine.identifier,
            InstanceCount=1,
            KeyName=key_record.key_name  # Ensure key_record has a key_name property.
        )
        for _ in range(runner_count)
    ]
    instance_ids = await asyncio.gather(*launch_tasks)
    launched_instance_ids.extend(instance_ids)
    
    # 5) Create Runner records (URL will be updated later by a background job).
    for instance_id in instance_ids:
        with Session(engine) as session:
            new_runner = Runner(
                machine_id=db_machine.id,
                image_id=db_image.id,
                user_id=None,           # No user assigned yet.
                key_id=key_record.id,     # Associate the runner with today's key.
                state="runner_starting",  # State will update once EC2 is running.
                url="",                 # Empty URL; background task will update it.
                token="",
                identifier=instance_id,
                external_hash=uuid.uuid4().hex,
                session_start=datetime.utcnow(),
                session_end=datetime.utcnow() + timedelta(minutes=10),
                created_by="system",
                modified_by="system"
            )
            session.add(new_runner)
            session.commit()
            session.refresh(new_runner)
            
            # Queue a Celery task to update runner state when EC2 is ready.
            update_runner_state.delay(new_runner.id, instance_id)
    
    return launched_instance_ids

async def shutdown_runners(launched_instance_ids: list):
    """Stop and then terminate all EC2 instances given in launched_instance_ids.
    Update the corresponding Runner record to "closed" after stopping and to
    "terminated" after termination.
    """
    for instance_id in launched_instance_ids:
        # 1) Stop the EC2 instance.
        stop_state = await Stop_EC2(instance_id)
        
        # After stopping, update the runner state to "closed".
        with Session(engine) as session:
            stmt = select(Runner).where(Runner.identifier == instance_id)
            runner = session.exec(stmt).first()
            if runner:
                runner.state = "closed"
                runner.ended_on = datetime.utcnow()
                session.add(runner)
                session.commit()
                print(f"Runner {runner.id} updated to 'closed'.")
            else:
                print(f"Runner with instance identifier {instance_id} not found (stop update).")
        
        # 2) Terminate the EC2 instance.
        terminate_state = await Terminate_EC2(instance_id)
        
        # After termination, update the runner state to "terminated".
        with Session(engine) as session:
            stmt = select(Runner).where(Runner.identifier == instance_id)
            runner = session.exec(stmt).first()
            if runner:
                runner.state = "terminated"
                session.add(runner)
                session.commit()
                print(f"Runner {runner.id} updated to 'terminated'.")
            else:
                print(f"Runner with instance identifier {instance_id} not found (terminate update).")

async def shutdown_all_runners():
    """Stop and then terminate all EC2 instances for runners that are not in the 'terminated' state.
    Uses the shutdown_runners function.
    """
    with Session(engine) as session:
        stmt = select(Runner).where(Runner.state != "terminated")
        runners_to_shutdown = session.exec(stmt).all()
        instance_ids = [runner.identifier for runner in runners_to_shutdown]
    await shutdown_runners(instance_ids)