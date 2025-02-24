from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.runner import Runner
from app.models.user import User
from app.business.encryption import encrypt_url
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class RunnerRequest(BaseModel):
    image_id: int
    env_data: Dict[str, Any]
    user_email: str

@router.post("/app_request", response_model=Dict[str, str])
def get_ready_runner(request: RunnerRequest, session: Session = Depends(get_session)):
    """
    Retrieve a runner with the "ready" state for the given image,
    assign it to the user based on user_email, update its environment data,
    set state to "setup", and return the encrypted runner URL.
    """
    # Query for a runner in "ready" state with the specified image_id.
    stmt_runner = select(Runner).where(Runner.state == "ready", Runner.image_id == request.image_id)
    runner = session.exec(stmt_runner).first()
    if not runner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ready runner available for that image"
        )
    
    # Look up the user by email.
    stmt_user = select(User).where(User.email == request.user_email)
    user_obj = session.exec(stmt_user).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    runner.user_id = user_obj.id
    runner.env_data = {"env": request.env_data}
    runner.state = "setup"
    
    session.add(runner)
    session.commit()
    session.refresh(runner)
    
    # Encrypt the runner URL for safe transport.
    encrypted_url = encrypt_url(runner.url)
    return {"encrypted_url": encrypted_url}