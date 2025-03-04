# app/business/script_management.py
"""Module for managing scripts and running them on runners via SSH."""

from sqlmodel import Session, select
from app.db.database import engine
from app.models.runner import Runner
from app.models.script import Script
from app.business.aws import SSH_Script
import jinja2
import asyncio

def render_script(template: str, context: dict) -> str:
    """
    Render the script template using the provided context.

    Uses Jinja2 for templating.
    """
    jinja_template = jinja2.Template(template)
    return jinja_template.render(**context)

def get_runner_key(runner_key_id: int) -> str:
    """
    Retrieve and decrypt the private key for the given runner's key record.

    Assumes there is a function get_key_by_id in key_management and a decrypt_text function.
    """
    from app.business.key_management import get_key_by_id  # Local import to avoid circular imports
    from app.business.encryption import decrypt_text

    key_record = get_key_by_id(runner_key_id)
    if not key_record:
        raise Exception("Key record not found")
    # Decrypt the key using the master encryption key.
    return decrypt_text(key_record.encrypted_key)

async def run_script_for_runner(event: str, runner_id: int) -> dict[str, str]:
    """
    Run scripts on runner based on event hook.

    Retrieve the script for the given event and runner's image,
    render it using the runner's env_data as context,
    and use SSH to run the script on the runner.
    Returns a dictionary with the output and error.
    """
    # Create a new session for lookup.
    with Session(engine) as session:
        runner = session.get(Runner, runner_id)
        if not runner:
            raise Exception("Runner not found")

        # Query for the script corresponding to the event and runner's image.
        stmt = select(Script).where(Script.event == event, Script.image_id == runner.image_id)
        script_record = session.exec(stmt).first()
        if not script_record:
            raise Exception(f"No script found for event '{event}' and image {runner.image_id}")

        # Create the context for the template by using the entire env_data
        # This allows the template to access both script_variables and env_vars
        template_context = runner.env_data

        # Render the script template using the context
        rendered_script = render_script(script_record.script, template_context)

    # Retrieve the private key using runner.key_id.
    private_key = get_runner_key(runner.key_id)

    # Use SSH_Script to run the rendered script on the runner.
    result = await SSH_Script(runner.url, private_key, rendered_script)
    return result
