"""Runners API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db.database import get_session
from app.models.runner import Runner
from app.models.runner_history import RunnerHistory
from app.schemas.runner import ExtendSessionRequest
from app.business.script_management import run_script_for_runner
from app.business.aws import Stop_EC2, Terminate_EC2  # Using AWS functions from cleanup_runners.py
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=list[Runner])
def read_runners(session: Session = Depends(get_session)):
    """Retrieve a list of all Runners."""
    runners = session.exec(select(Runner)).all()
    return runners

@router.get("/{runner_id}", response_model=Runner)
def read_runner(runner_id: int, session: Session = Depends(get_session)):
    """Retrieve a single Runner by ID."""
    runner = session.get(Runner, runner_id)
    if not runner:
        raise HTTPException(status_code=404, detail="Runner not found")
    return runner

@router.put("/extend_session", response_model=str)
def extend_runner_session(
    extend_req: ExtendSessionRequest,
    session: Session = Depends(get_session)
    ):
    """Update a runner's session_end by adding extra time."""
    runner = session.get(Runner, extend_req.runner_id)
    if not runner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Runner not found"
        )

    # Calculate the new session_end by adding extra_time.
    extension = timedelta(minutes=extend_req.extra_time)
    new_session_end = runner.session_end + extension

    # Check that total session duration does not exceed 3 hours.
    total_duration = new_session_end - runner.session_start
    if total_duration > timedelta(hours=3):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extension would exceed maximum allowed session time of 3 hours."
        )

    # Save the old session_end for history logging.
    old_session_end = runner.session_end

    # Update the runner's session_end.
    runner.session_end = new_session_end
    session.add(runner)

    # Create a new runner_history record logging this extension event.
    event_data = {
        "extra_time": extend_req.extra_time,
        "old_session_end": old_session_end.isoformat(),
        "new_session_end": new_session_end.isoformat()
    }
    new_history = RunnerHistory(
        runner_id=runner.id,
        event_name="session_extension",
        event_data=event_data,
        created_by="system",  # or the authenticated user's identifier
        modified_by="system"
    )
    session.add(new_history)

    session.commit()
    session.refresh(runner)
    return "Session extended successfully"

class TerminateRunnerRequest(BaseModel):
    """Request model for the terminate_runner endpoint."""

    runner_id: int

@router.post("/terminate", response_model=dict[str, str])
async def terminate_runner(
    request: TerminateRunnerRequest,
    session: Session = Depends(get_session)
):
    """Manually terminate a runner and run the on_terminate script."""
    # Check if the runner exists
    runner = session.get(Runner, request.runner_id)
    if not runner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Runner with ID {request.runner_id} not found"
        )

    # Check if the runner is already terminated
    if runner.state in ["terminated", "closed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Runner with ID {request.runner_id} is already terminated"
        )

    # Update runner state to "terminating"
    old_state = runner.state
    runner.state = "terminating"
    session.add(runner)

    # Create a runner history record for this termination event
    event_data = {
        "old_state": old_state,
        "new_state": "terminating",
        "manual_termination": True
    }
    new_history = RunnerHistory(
        runner_id=runner.id,
        event_name="manual_termination_initiated",
        event_data=event_data,
        created_by="system",
        modified_by="system"
    )
    session.add(new_history)
    session.commit()

    try:
        # Run the on_terminate script
        try:
            script_result = await run_script_for_runner("on_terminate", runner.id)

            # Add script execution history
            script_event_data = {
                "script_event": "on_terminate",
                "result": "success" if "error" not in script_result else "error",
                "details": script_result.get("output", "") if "error" not in script_result else script_result.get("error", "")
            }
            script_history = RunnerHistory(
                runner_id=runner.id,
                event_name="script_execution",
                event_data=script_event_data,
                created_by="system",
                modified_by="system"
            )
            session.add(script_history)
            session.commit()

            if "error" in script_result:
                logger.error(f"Error running on_terminate script for runner {runner.id}: {script_result['error']}")
                # Continue with termination even if script fails
        except Exception as e:
            logger.error(f"Error running on_terminate script for runner {runner.id}: {e!s}")
            # Continue with termination even if script fails

        # Stop and Terminate the EC2 instance - use await with async functions
        try:
            await Stop_EC2(runner.identifier)  # First stop the instance
            await Terminate_EC2(runner.identifier)  # Then terminate it
            logger.info(f"EC2 instance {runner.identifier} stopped and terminated")

            # Add EC2 termination history
            ec2_event_data = {
                "ec2_identifier": runner.identifier,
                "result": "success"
            }
            ec2_history = RunnerHistory(
                runner_id=runner.id,
                event_name="ec2_termination",
                event_data=ec2_event_data,
                created_by="system",
                modified_by="system"
            )
            session.add(ec2_history)
        except Exception as e:
            error_msg = f"Failed to terminate EC2 instance {runner.identifier}: {e!s}"
            logger.error(error_msg)

            # Add EC2 termination failure history
            ec2_event_data = {
                "ec2_identifier": runner.identifier,
                "result": "error",
                "error": str(e)
            }
            ec2_history = RunnerHistory(
                runner_id=runner.id,
                event_name="ec2_termination_error",
                event_data=ec2_event_data,
                created_by="system",
                modified_by="system"
            )
            session.add(ec2_history)
            session.commit()

            # Continue and update the runner state anyway to avoid orphaned runners

        # Update runner state to "terminated"
        runner.state = "terminated"
        # Use ended_on instead of termination_time
        runner.ended_on = datetime.utcnow()
        session.add(runner)

        # Add final termination history
        final_event_data = {
            "initial_state": old_state,
            "final_state": "terminated",
            "termination_time": datetime.utcnow().isoformat()
        }
        final_history = RunnerHistory(
            runner_id=runner.id,
            event_name="termination_completed",
            event_data=final_event_data,
            created_by="system",
            modified_by="system"
        )
        session.add(final_history)
        session.commit()

        return {"status": "success", "message": "Runner terminated successfully"}
    except Exception as e:
        # If something goes wrong, log the error and return an error response
        error_msg = f"Failed to terminate runner: {e!s}"
        logger.error(error_msg)

        # Add error history
        error_event_data = {
            "error": str(e)
        }
        error_history = RunnerHistory(
            runner_id=runner.id,
            event_name="termination_error",
            event_data=error_event_data,
            created_by="system",
            modified_by="system"
        )
        session.add(error_history)
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        ) from e
