"""Schema for username/password auth objects."""
from pydantic import BaseModel

class PasswordAuth(BaseModel):
    """Auth object to carry username and password in request."""

    email: str
    password: str
    ip_address: str | None = None
    user_agent: str | None = None
