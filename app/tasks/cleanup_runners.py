# app/tasks/cleanup_runners.py

from datetime import datetime
from sqlmodel import Session, select
from celery.utils.log import get_task_logger
from app.celery_app import celery_app
from app.db.database import engine
from app.models.runner import Runner
from app.models.runner_history import RunnerHistory
from app.business.aws import Stop_EC2

logger = get_task_logger(__name__)

@celery_app.task
def cleanup_active_runners():
    logger.info("Starting cleanup of active runners whose session_end has passed.")
    now = datetime.utcnow()

    with Session(engine) as session:
        # Query all runners that are active and whose session_end is in the past
        results = session.exec(
            select(Runner).where(
                Runner.state == "active",
                Runner.session_end < now
            )
        ).all()

        count = 0
        for runner in results:
            logger.info(f"Shutting down runner {runner.id} (EC2 instance {runner.identifier})")

            # 1) Stop or Terminate the instance
            Stop_EC2(runner.identifier)  # or Terminate_EC2 if you want to fully kill it

            # 2) Update the runner record
            runner.state = "closed"
            runner.ended_on = now
            session.add(runner)

            # 3) Create a runner history record
            event_data = {
                "previous_state": "active",
                "new_state": "closed",
                "shut_down_time": now.isoformat()
            }
            history_record = RunnerHistory(
                runner_id=runner.id,
                event_name="runner_shutdown",
                event_data=event_data,
                created_by="system",
                modified_by="system"
            )
            session.add(history_record)

            count += 1

        # Commit the changes once after processing everything
        session.commit()

    logger.info(f"Cleanup complete. Stopped {count} runners.")