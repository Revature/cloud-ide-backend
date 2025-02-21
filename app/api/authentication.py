# app/api/authentication.py
# https://workos.com/docs/reference/sso/profile/get-user-profile
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from workos import WorkOSClient

# # Use HTTPBearer to extract the token from the Authorization header
oauth2_scheme = HTTPBearer()

# Initialize the WorkOSClient using environment variables (or hardcode for testing)
workos_client = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"), 
    client_id=os.getenv("WORKOS_CLIENT_ID")
)

def verify_workos_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        # Use the WorkOS client to get the user's profile
        profile = workos_client.sso.get_profile(access_token=token)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired WorkOS token."
        )