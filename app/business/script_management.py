# app/business/script_management.py
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
    Retrieves and decrypts the private key for the given runner's key record.
    Assumes there is a function get_key_by_id in key_management and a decrypt_text function.
    """
    from app.business.key_management import get_key_by_id  # Local import to avoid circular imports
    from app.business.encryption import decrypt_text

    key_record = get_key_by_id(runner_key_id)
    if not key_record:
        raise Exception("Key record not found")
    # Decrypt the key using the master encryption key.
    return decrypt_text(key_record.encrypted_key)

def run_script_for_runner(event: str, runner_id: int) -> dict[str, str]:
    """
    Retrieves the script for the given event and runner's image,
    renders it using the runner's environment data, and uses SSH to run the script.
    
    Parameters:
      - event: The lifecycle event (e.g., "on_create", "on_connect", "on_disconnect", "on_terminate").
      - runner_id: The ID of the runner on which to run the script.
    
    Returns:
      A dictionary with the SSH command output and error, e.g.:
        {"Output": "...", "Error": "..."}
    """
    # Retrieve runner and script records.
    with Session(engine) as session:
        runner = session.get(Runner, runner_id)
        if not runner:
            raise Exception("Runner not found")
        
        # Query for a script for the given event and runner's image.
        stmt = select(Script).where(Script.event == event, Script.image_id == runner.image_id)
        script_record = session.exec(stmt).first()
        if not script_record:
            raise Exception(f"No script found for event '{event}' for image ID {runner.image_id}")
        
        # Render the script template using runner.env_data as context.
        # The script template should contain placeholders matching keys in runner.env_data.
        rendered_script = render_script(script_record.script, runner.env_data)
    
    # Get the runner's public IP. (Assuming runner.url stores the public IP.)
    runner_ip = runner.url
    if not runner_ip:
        raise Exception("Runner IP not set")
    
    # Retrieve and decrypt the private key for the runner.
    private_key = get_runner_key(runner.key_id)
    
    # Run the script on the remote runner.
    # SSH_Script is asynchronous; we run it synchronously here.
    result = asyncio.run(SSH_Script(runner_ip, private_key, rendered_script))
    return result