from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session, engine
from app.models.runner import Runner
from app.models.user import User
from app.models.image import Image
from app.business.encryption import encrypt_url
from pydantic import BaseModel
from typing import Dict, Any
from app.business.runner_management import launch_runners
import asyncio

router = APIRouter()

class RunnerRequest(BaseModel):
    image_id: int
    env_data: Dict[str, Any]
    user_email: str

@router.post("/app_request", response_model=Dict[str, str])
async def get_ready_runner(request: RunnerRequest, session: Session = Depends(get_session)):
    """
    Retrieve a runner with the "ready" state for the given image and assign it to a user.
    
    If the image's runner_pool_size is 0:
      - Launch a new runner and wait until its state becomes "ready" before proceeding.
    Otherwise:
      - Use an existing ready runner.
    
    The runner's environment data is updated, its state is set to "setup",
    and the encrypted runner URL is returned.
    """
    # Retrieve the image record.
    stmt_image = select(Image).where(Image.id == request.image_id)
    db_image = session.exec(stmt_image).first()
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    
    # Determine which runner to use.
    if db_image.runner_pool_size == 0:
        # Launch a new runner and wait for it to be ready.
        instance_ids = await launch_runners(db_image.identifier, 1)
        instance_id = instance_ids[0]
        stmt_runner = select(Runner).where(Runner.identifier == instance_id)
        runner = session.exec(stmt_runner).first()
        
        # Poll up to 60 seconds (12 attempts, every 5 seconds)
        # for _ in range(12):
        #     with Session(engine) as poll_session:
        #         stmt_runner = select(Runner).where(Runner.identifier == instance_id)
        #         runner = poll_session.exec(stmt_runner).first()
        #     if runner and runner.state == "ready":
        #         break
        #     await asyncio.sleep(5)
        # if not runner or runner.state != "ready":
        #     raise HTTPException(status_code=500, detail="Runner did not become ready in time")
    else:
        # Query for a runner in "ready" state for the given image.
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
    
    # Update the runner: assign the user, update environment data, and change state to "setup".
    runner.user_id = user_obj.id
    runner.env_data = {"env": request.env_data}
    runner.state = "setup"
    
    session.add(runner)
    session.commit()
    session.refresh(runner)
    
    # Encrypt the runner URL for safe transport.
    # encrypted_url = encrypt_url(runner.url)
    
    # If the pool size is not zero, launch a new runner asynchronously to replenish the pool.
    if db_image.runner_pool_size != 0:
        asyncio.create_task(launch_runners(db_image.identifier, 1))
    
    # return {"encrypted_url": encrypted_url}
    return {"url": runner.url}