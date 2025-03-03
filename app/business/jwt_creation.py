# app/business/jwt_creation.py

import os
import jwt
from datetime import datetime, timedelta

def create_jwt_token(runner_ip: str) -> str:
    """
    Create a JWT token for the given runner_id.
    
    The token will expire in 1 hour.
    """
    secret = os.getenv("JWT_SECRET", "default_secret")  # Use a secure secret in production!
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    payload = {
        "runner_ip": runner_ip
    }
    token = jwt.encode(payload, secret, algorithm=algorithm)
    # jwt.encode may return a string or bytes depending on the version of PyJWT
    return token if isinstance(token, str) else token.decode("utf-8")