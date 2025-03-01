"""Application request handling API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timedelta
from app.db.database import get_session, engine
from app.models.runner import Runner
from app.models.user import User
from app.models.image import Image
from app.business.encryption import encrypt_text
from app.business.runner_management import launch_runners
from app.business.script_management import run_script_for_runner  # Script management layer
import asyncio

router = APIRouter()

class RunnerRequest(BaseModel):
    """Request model for the get_ready_runner endpoint."""

    image_id: int
    env_data: Dict[str, Any]
    user_email: str
    session_time: int  # in minutes, limit to 3 hours
    runner_type: str   # temporary/permanent

@router.post("/", response_model=Dict[str, str])
async def get_ready_runner(request: RunnerRequest, session: Session = Depends(get_session)):
    """
    Retrieve a runner with the "ready" state for the given image and assign it to a user.

    If the user already has an "alive" runner for the image, update its session_end.
    Otherwise, if no ready runner is available, launch a new one.

    The runner's environment data is updated, its state is set to "awaiting_client",
    and the URL is returned. Also, the appropriate script is executed for the
    "on_awaiting_client" event.
    """
    # Retrieve the image record.
    stmt_image = select(Image).where(Image.id == request.image_id)
    db_image = session.exec(stmt_image).first()
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    # Look up the user by email.
    stmt_user = select(User).where(User.email == request.user_email)
    user_obj = session.exec(stmt_user).first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if the user already has an alive runner for the requested image.
    stmt_runner = select(Runner).where(
        Runner.state.in_(["active", "ready"]),
        Runner.image_id == request.image_id,
        Runner.user_id == user_obj.id
    )
    existing_runner = session.exec(stmt_runner).first()

    if existing_runner:
        if request.session_time > 180:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session time cannot exceed 3 hours.")
        # Update session_end for the existing runner.
        existing_runner.session_end = existing_runner.session_start + timedelta(minutes=request.session_time)
        session.add(existing_runner)
        session.commit()
        session.refresh(existing_runner)
        return {"url": f"http://{existing_runner.url}:3000", "runner_id": str(existing_runner.id)}

    # No alive runner found; select a ready runner or launch a new one.
    if db_image.runner_pool_size == 0:
        # Launch a new runner and wait for it to be ready.
        instance_ids = await launch_runners(db_image.identifier, 1)
        instance_id = instance_ids[0]
        stmt_runner = select(Runner).where(Runner.identifier == instance_id)
        runner = session.exec(stmt_runner).first()
        # Poll up to 60 seconds (12 attempts, every 5 seconds).
        for _ in range(12):
            with Session(engine) as poll_session:
                stmt_runner = select(Runner).where(Runner.identifier == instance_id)
                runner = poll_session.exec(stmt_runner).first()
            if runner and runner.state == "ready":
                break
            await asyncio.sleep(5)
        if not runner or runner.state != "ready":
            raise HTTPException(status_code=500, detail="Runner did not become ready in time")
    else:
        # Query for a runner in "ready" state for the given image.
        stmt_runner = select(Runner).where(Runner.state == "ready", Runner.image_id == request.image_id)
        runner = session.exec(stmt_runner).first()
        if not runner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No ready runner available for that image"
            )

    # Update the runner: assign the user, update environment data, and change state to "awaiting_client".
    runner.user_id = user_obj.id
    runner.env_data = {"env": request.env_data}
    runner.state = "awaiting_client"

    if request.session_time > 180:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session time cannot exceed 3 hours.")

    runner.session_start = datetime.utcnow()
    runner.session_end = runner.session_start + timedelta(minutes=request.session_time)

    session.add(runner)
    session.commit()
    session.refresh(runner)

    # Optionally, launch a new runner asynchronously to replenish the pool.
    if db_image.runner_pool_size != 0:
        asyncio.create_task(launch_runners(db_image.identifier, 1))

    # Execute the script for the "awaiting_client" event.
    try:
        script_result = await run_script_for_runner("on_awaiting_client", runner.id)
        print(f"Script executed for runner {runner.id}: {script_result}")
    except Exception as e:
        print(f"Error executing script for runner {runner.id}: {e}")

    return {"url": f"http://{runner.url}:3000", "runner_id": str(runner.id)}
