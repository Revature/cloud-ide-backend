"""Authorization route for acquiring bearer tokens."""
import os
from pydantic import BaseModel
from workos import WorkOSClient, exceptions
from app.api.authentication import password_authentication
from app.schemas.auth_schema import PasswordAuth
from fastapi import APIRouter, Request, Response

workos = WorkOSClient(api_key=os.getenv("WORKOS_API_KEY"), client_id=os.getenv("WORKOS_CLIENT_ID"))

router = APIRouter()

@router.post("/machine_auth", status_code=200)
def machine_auth(request: Request, passwordAuth: PasswordAuth, response: Response):
    """Authenticate with username and password, receive access token in Access-Token header."""
    passwordAuth.ip_address = request.client.host
    passwordAuth.user_agent = request.headers.get("User-Agent")

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
