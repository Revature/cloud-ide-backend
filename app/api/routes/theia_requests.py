from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.database import get_session
from app.models.runner import Runner
from app.models.runner_history import RunnerHistory
from app.business.script_management import run_script_for_runner  # Script management layer

router = APIRouter()

class RunnerStateUpdate(BaseModel):
    url: str
    state: str  # e.g., "app_starting", "awaiting_client", "active", "disconnecting"
    token: Optional[str] = None

@router.post("/update_state", response_model=Runner)
async def update_runner_state_endpoint(
    update: RunnerStateUpdate,
    session: Session = Depends(get_session)
):
    """
    Endpoint for Theia to report state changes.
    The request should include:
      - url: The URL of the runner (from AWS)
      - state: The new state
      - token (optional): an updated token when applicable.
    
    For each state update, a RunnerHistory record is created. Additionally,
    if the state change corresponds to one of our script events, the corresponding
    script is executed on the runner.
    
    Script event mapping:
      - app_starting  → on_create
      - ready         → no script
      - awaiting_client → on_awaiting_client
      - active        → on_connect
      - disconnecting → on_disconnect
      - on_terminate is handled elsewhere.
    """
    stmt = select(Runner).where(Runner.url == update.url)
    runner = session.exec(stmt).first()
    if not runner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Runner not found")
    
    # Prepare common event_data.
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "new_state": update.state
    }
    
    script_event = None  # Default: no script execution.
    
    # Map runner state to script event.
    if update.state == "app_starting":
        runner.state = "app_starting"
        event_name = "runner_app_starting"
        script_event = "on_create"
    elif update.state == "ready":
        runner.state = "ready"
        event_name = "runner_ready"
    elif update.state == "awaiting_client":
        runner.state = "awaiting_client"
        event_name = "runner_awaiting_client"
        script_event = "on_awaiting_client"
    elif update.state == "active":
        runner.state = "active"
        event_name = "runner_active"
        script_event = "on_connect"
        if update.token:
            runner.token = update.token
            event_data["token"] = update.token
    elif update.state == "disconnecting":
        runner.state = "disconnecting"
        event_name = "runner_disconnecting"
        script_event = "on_disconnect"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid state: {update.state}"
        )
    
    # Update the runner.
    session.add(runner)
    session.commit()
    session.refresh(runner)
    
    # Create a runner history record.
    new_history = RunnerHistory(
        runner_id=runner.id,
        event_name=event_name,
        event_data=event_data,
        created_by="system",
        modified_by="system"
    )
    session.add(new_history)
    session.commit()
    
    # Execute the script for this event if applicable.
    if script_event:
        try:
            script_result = await run_script_for_runner(script_event, runner.id)
            new_history.event_data["script_result"] = script_result
            session.add(new_history)
            session.commit()
        except Exception as e:
            print(f"Error executing script for runner {runner.id}: {e}")
    
    return runner
