from app.celery_app import celery_app
from app.db.database import engine
from sqlmodel import Session
from app.models.runner import Runner
from app.business.aws import wait_for_instance_running  # Synchronous waiter function

@celery_app.task
def update_runner_state(runner_id: int, instance_id: str):
    """
    Wait for the EC2 instance to be running and update the runner's state to "ready".
    """
    # Block until the instance is running (this is synchronous)
    wait_for_instance_running(instance_id)
    
    # Once the instance is running, update the runner record in the DB.
    with Session(engine) as session:
        runner = session.get(Runner, runner_id)
        if runner:
            runner.state = "ready"
            session.add(runner)
            session.commit()