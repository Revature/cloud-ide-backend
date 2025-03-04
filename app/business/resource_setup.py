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
        awaiting_client_script = session.exec(stmt_script).first()
        if not awaiting_client_script:
            awaiting_client_script = Script(
                name="Git Clone Script",
                description="Clones a repository specified in runner env_data under 'repo_url'",
                event="on_awaiting_client",
                image_id=db_image.id,
                script=r"""#!/bin/bash
# Script to set up GitHub credentials and clone the repository

set -e  # Exit on error
echo "Setting up environment and cloning repository..."

# Extract variables from script_vars and env_vars
REPO_URL="{{ script_vars.git_url }}"
REPO_NAME="{{ script_vars.git_repo_name }}"
GIT_TOKEN="{{ env_vars.git_token }}"
GIT_USERNAME="{{ env_vars.git_username }}"

# Set up GitHub credentials as environment variables for later use
if [ -n "$GIT_TOKEN" ] && [ -n "$GIT_USERNAME" ]; then
    # Store credentials in the user's environment
    echo "export GITHUB_TOKEN=$GIT_TOKEN" >> /home/ubuntu/.bashrc
    echo "export GITHUB_USERNAME=$GIT_USERNAME" >> /home/ubuntu/.bashrc

    # Create a local environment file that can be sourced later
    echo "GITHUB_TOKEN=$GIT_TOKEN" > /home/ubuntu/.github_env
    echo "GITHUB_USERNAME=$GIT_USERNAME" >> /home/ubuntu/.github_env
    chmod 600 /home/ubuntu/.github_env
    chown ubuntu:ubuntu /home/ubuntu/.github_env

    # Set git configuration
    sudo -u ubuntu git config --global user.name "$GIT_USERNAME"
    sudo -u ubuntu git config --global user.email "$GIT_USERNAME@users.noreply.github.com"

    echo "GitHub credentials set up successfully."
else
    echo "WARNING: GitHub credentials not provided. Repository will be cloned, but changes cannot be saved later."
fi

# Clone the repository
if [ -n "$REPO_URL" ] && [ -n "$REPO_NAME" ]; then
    # Check if we have a token to use
    if [ -n "$GIT_TOKEN" ]; then
        # Use token for authentication
        AUTH_URL=$(echo "$REPO_URL" | sed "s/https:\/\//https:\/\/$GIT_TOKEN@/")
        sudo -u ubuntu git clone "$AUTH_URL" "/home/ubuntu/$REPO_NAME"
    else
        # Clone without authentication
        sudo -u ubuntu git clone "$REPO_URL" "/home/ubuntu/$REPO_NAME"
    fi

    echo "Repository cloned successfully to /home/ubuntu/$REPO_NAME"
else
    echo "ERROR: Repository URL or name not provided. Cannot clone repository."
    exit 1
fi

# Success
echo "Environment setup completed successfully."
exit 0""",
                created_by="system",
                modified_by="system"
            )
            session.add(awaiting_client_script)
            session.commit()
            session.refresh(awaiting_client_script)

        # 5) Fetch or create default Script for the "on_terminate" event
        stmt_script = select(Script).where(Script.event == "on_terminate", Script.image_id == db_image.id)
        termination_script = session.exec(stmt_script).first()
        if not termination_script:
            termination_script = Script(
                name="GitHub Save Script",
                description="Commits and pushes changes to GitHub on termination",
                event="on_terminate",
                image_id=db_image.id,
                script=r"""#!/bin/bash
# Script to commit and push changes on runner termination

set -e  # Exit on error
echo "Starting GitHub save operations..."

# Extract variables from script_vars
REPO_NAME="{{ script_vars.git_repo_name }}"
REPO_URL="{{ script_vars.git_url }}"
REPO_PATH="/home/ubuntu/$REPO_NAME"

# Load environment variables that were set during on_awaiting_client
# First try .github_env, then fall back to .bashrc
if [ -f "/home/ubuntu/.github_env" ]; then
    source /home/ubuntu/.github_env
else
    # Extract tokens from bashrc as a fallback
    GITHUB_TOKEN=$(grep "GITHUB_TOKEN" /home/ubuntu/.bashrc | cut -d'=' -f2 | tr -d '"')
    GITHUB_USERNAME=$(grep "GITHUB_USERNAME" /home/ubuntu/.bashrc | cut -d'=' -f2 | tr -d '"')
fi

# Set a default commit message
COMMIT_MESSAGE="Auto-save from cloud IDE on $(date +'%Y-%m-%d %H:%M:%S')"

# Check if required variables are set
if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_USERNAME" ]; then
    echo "ERROR: GitHub credentials not found in environment variables. Skipping git operations."
    exit 0  # Exit without error to allow runner termination to proceed
fi

# Check if repository path exists
if [ ! -d "$REPO_PATH" ]; then
    echo "ERROR: Repository directory not found at $REPO_PATH. Skipping git operations."
    exit 0
fi

cd "$REPO_PATH" || exit 1

# Check if there are any changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit. Exiting."
    exit 0
fi

# Configure the repository with authentication
echo "Configuring repository with authentication..."
AUTH_REMOTE_URL=$(echo "$REPO_URL" | sed "s/https:\/\//https:\/\/$GITHUB_TOKEN@/")
git remote set-url origin "$AUTH_REMOTE_URL"

# Add all changes
git add --all

# Commit changes
git commit -m "$COMMIT_MESSAGE"

# Push to the repository
echo "Pushing changes to repository..."
# Try common branch names, or push to the current branch
git push origin main || git push origin master || git push origin HEAD

echo "Successfully pushed changes to repository"
echo "GitHub operations completed successfully."
exit 0""",
                created_by="system",
                modified_by="system"
            )
            session.add(termination_script)
            session.commit()
            session.refresh(termination_script)

        return Resources(
            system_user_email=system_user.email,
            machine_id=db_machine.id,
            image_identifier=db_image.identifier,
            runner_pool_size=db_image.runner_pool_size
        )
