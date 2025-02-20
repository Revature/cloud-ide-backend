from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta
from app.db.database import get_session
from app.models.runner import Runner
from app.models.runner_history import RunnerHistory
from app.schemas.runner import ExtendSessionRequest 

router = APIRouter()

@router.get("/", response_model=List[Runner]) 
def read_runners(session: Session = Depends(get_session)):
    """
    Retrieve a list of all Runners.
    """
    runners = session.exec(select(Runner)).all()
    return runners

@router.get("/{runner_id}", response_model=Runner)
def read_runner(runner_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single Runner by ID.
    """
    runner = session.get(Runner, runner_id)
    if not runner:
        raise HTTPException(status_code=404, detail="Runner not found")
    return runner

@router.put("/{runner_id}", response_model=Runner)
def extend_runner_session(
    runner_id: int,
    extend_req: ExtendSessionRequest,
    session: Session = Depends(get_session)
):
    # Retrieve the runner record.
    runner = session.get(Runner, runner_id)
    if not runner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Runner not found"
        )
    
    # Calculate the new session_end by adding the extra time.
    extension = timedelta(minutes=extend_req.extra_time)
    new_session_end = runner.session_end + extension
    
    # Check that the total session duration (from session_start to new_session_end) does not exceed 3 hours.
    total_duration = new_session_end - runner.session_start
    if total_duration > timedelta(hours=3):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extension would exceed maximum allowed session time of 3 hours."
        )
    
    # Save the old session_end for logging.
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
        runner_id=runner_id,
        event_name="session extension",
        event_data=event_data,
        created_by="system",    # or the authenticated user's identifier
        modified_by="system"
    )
    session.add(new_history)
    
    session.commit()
    session.refresh(runner)
    return runner