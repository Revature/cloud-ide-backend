# app/business/resource_setup.py
"""Module for setting up default resources in the database."""

from dataclasses import dataclass
from sqlmodel import Session, select
from app.db.database import engine
from app.models import User, Machine, Image, Script
from datetime import datetime

@dataclass
class Resources:
    """Dataclass for storing default resources."""

    system_user_email: str
    machine_id: int
    image_identifier: str
    runner_pool_size: int

def setup_resources():
    """
    Fetch or create default User, Machine, Image, and Script.

    Returns a Resources dataclass with the necessary values.
    """
    with Session(engine) as session:
        # 1) Fetch or create a default user.
        stmt_user = select(User).where(User.email == "ashoka.shringla@revature.com")
        system_user = session.exec(stmt_user).first()
        if not system_user:
            system_user = User(
                first_name="Ashoka",
                last_name="Shringla",
                email="ashoka.shringla@revature.com",
                created_by="system",
                modified_by="system"
            )
            session.add(system_user)
            session.commit()
            session.refresh(system_user)

        # 2) Fetch or create default Machine.
        stmt_machine = select(Machine).where(Machine.identifier == "t2.medium")
        db_machine = session.exec(stmt_machine).first()
        if not db_machine:
            db_machine = Machine(
                name="t2.medium",
                identifier="t2.medium",  # Use a valid EC2 instance type here
                cpu_count=2,
                memory_size=4096,
                storage_size=20,
                created_by="system",
                modified_by="system"
            )
            session.add(db_machine)
            session.commit()
            session.refresh(db_machine)

        # 3) Fetch or create default Image.
        stmt_image = select(Image).where(Image.identifier == "ami-0bbfffa970b0280da")
        db_image = session.exec(stmt_image).first()
        if not db_image:
            db_image = Image(
                name="sample-id-image",
                description="An AMI for testing",
                identifier="ami-0bbfffa970b0280da",
                runner_pool_size=1,  # Example pool size
                machine_id=db_machine.id,
                created_by="system",
                modified_by="system"
            )
            session.add(db_image)
            session.commit()
            session.refresh(db_image)

        # 4) Fetch or create default Script for the "on_awaiting_client" event.
        stmt_script = select(Script).where(Script.event == "on_awaiting_client", Script.image_id == db_image.id)
        default_script = session.exec(stmt_script).first()
        if not default_script:
            default_script = Script(
                name="Git Clone Script",
                description="Clones a repository specified in runner env_data under 'repo_url'",
                event="on_awaiting_client",
                image_id=db_image.id,
                script="""#!/bin/bash
# Git clone script

if [ -z "{{ repo_url }}" ]; then
    echo "Error: repository URL not provided."
    exit 1
fi

if [ -z "{{ repo_name }}" ]; then
    echo "Error: repository name not provided."
    exit 1
fi

rm -rf /home/ubuntu/{{ repo_name }}
git clone "{{ repo_url }}" /home/ubuntu/{{ repo_name }}
if [ $? -eq 0 ]; then
    echo "Repository cloned successfully."
else
    echo "Failed to clone repository."
    exit 1
fi""",
                created_by="system",
                modified_by="system"
            )
            session.add(default_script)
            session.commit()
            session.refresh(default_script)

        return Resources(
            system_user_email=system_user.email,
            machine_id=db_machine.id,
            image_identifier=db_image.identifier,
            runner_pool_size=db_image.runner_pool_size
        )
