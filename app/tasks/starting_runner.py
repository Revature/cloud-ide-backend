from datetime import datetime
from app.celery_app import celery_app
from app.db.database import engine
from sqlmodel import Session
from app.models.runner import Runner
from app.models.runner_history import RunnerHistory
from app.business.aws import wait_for_instance_running  # Synchronous waiter function

@celery_app.task
def update_runner_state(runner_id: int, instance_id: str):
    """
    Wait for the EC2 instance to become 'running' and update
    the runner's state to 'ready', recording the event in RunnerHistory.
    """
    try:
        # 1. Wait for instance to be running (blocking call)
        wait_for_instance_running(instance_id)

        # 2. Update the runner in the database
        with Session(engine) as session:
            runner = session.get(Runner, runner_id)
            if runner:
                runner.state = "ready"
                session.add(runner)
                session.commit()

                # 3. Create a new RunnerHistory record
                event_data = {
                    "starting_time": (
                        runner.session_start.isoformat()
                        if runner.session_start
                        else "No session_start recorded"
                    ),
                    "ready_time": datetime.utcnow().isoformat(),
                    "instance_id": instance_id
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