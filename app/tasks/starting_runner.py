# tasks/starting_runner.py
import asyncio
from datetime import datetime
from app.celery_app import celery_app
from app.db.database import engine
from sqlmodel import Session
from app.models.runner import Runner
from app.models.runner_history import RunnerHistory
from app.business.aws import wait_for_instance_running, Describe_EC2

@celery_app.task(name="app.tasks.starting_runner.update_runner_state")
def update_runner_state(runner_id: int, instance_id: str):
    """
    Wait for the EC2 instance to become 'running', update the runner's state to 'ready',
    set the runner's URL, and record the event in RunnerHistory.
    """
    try:
        # 1. Wait for the instance to be running (blocking call)
        wait_for_instance_running(instance_id)

        # 2. Retrieve the public IP of the EC2 instance.
        # Since Describe_EC2 is async, run it synchronously.
        public_ip = asyncio.run(Describe_EC2(instance_id))

        # 3. Update the runner in the database.
        with Session(engine) as session:
            runner = session.get(Runner, runner_id)
            if runner:
                runner.state = "ready"
                runner.url = public_ip
                session.add(runner)
                session.commit()

                # 4. Create a new RunnerHistory record.
                event_data = {
                    "starting_time": runner.session_start.isoformat() if runner.session_start else "No session_start recorded",
                    "ready_time": datetime.utcnow().isoformat(),
                    "instance_id": instance_id,
                    "public_ip": public_ip
                }
                new_history = RunnerHistory(
                    runner_id=runner_id,
                    event_name="runner_ready",
                    event_data=event_data,
                    created_by="system",
                    modified_by="system"
                )
                session.add(new_history)
                session.commit()

                print(f"Runner {runner_id} updated to 'ready' and history record created.")
            else:
                print(f"Runner {runner_id} not found in the database.")
    except Exception as e:
        print(f"Error in update_runner_state: {e}")
        raise
