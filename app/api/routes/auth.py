"""Authorization route for acquiring bearer tokens."""
import os
from pydantic import BaseModel
from workos import WorkOSClient, exceptions
from app.api.authentication import password_authentication
from fastapi import APIRouter, Request, Response

workos = WorkOSClient(api_key=os.getenv("WORKOS_API_KEY"), client_id=os.getenv("WORKOS_CLIENT_ID"))

router = APIRouter()


class PasswordAuth(BaseModel):
    """Auth object to carry username and password in request."""

    email: str
    password: str
    ip_address: str | None
    user_agent: str | None

    def __init__(self, email, password):
        """Initialize required params."""
        self.email = email
        self.password = password


@router.post("/machine_auth", status_code=200)
def machine_auth(request: Request, passwordAuth: PasswordAuth, response: Response):
    """Authenticate with username and password, receive access token in Access-Token header."""
    request.ip_address = request.client.host
    request.user_agent = request.headers.get("User-Agent")

    try:
        access_token = password_authentication(passwordAuth)
        response.headers["Access-Token"] = access_token
        response.status_code = 200
        return '{"status": 200}'
    except exceptions.BadRequestException:
        response.status_code = 401
        return '{"error": "Unauthorized: bad credentials"}'
    except Exception:
        response.status_code = 500
        return '{"error": "Internal Server Error"}'
