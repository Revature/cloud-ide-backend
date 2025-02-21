from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.runner import Runner

router = APIRouter()

@router.post("/app_request", response_model=Runner)
def get_ready_runner(session: Session = Depends(get_session)):
    """
    Retrieve a runner with the "ready" state.
    """
    stmt = select(Runner).where(Runner.state == "ready")
    ready_runner = session.exec(stmt).first()
    if not ready_runner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No ready runner available"
        )
    
    ready_runner.state = "setup"
    session.add(ready_runner)
    session.commit()
    session.refresh(ready_runner)
    
    return ready_runner