from datetime import time
import os
from workos import WorkOSClient, exceptions
from app.api.routes.auth import PasswordAuth
from app.business.pkce import decode_signed_token
from app.models.workos_session import WorkosSession, create_workos_session, get_refresh_token, refresh_session

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"), 
    client_id=os.getenv("WORKOS_CLIENT_ID")
)

# Moving this behavior into a decorator to apply to routes would be best
def token_authentication(access_token: str):
    # check access token
    decoded_token = decode_signed_token(access_token)
    if(decoded_token.get('exp') >= int(time.time())):
        # Try refreshing access token - this will throw a workos.exceptions.BadRequestException if it fails
        refresh_response = workos.user_management.authenticate_with_refresh_token(refresh_token = get_refresh_token(access_token))
        refresh_session(refresh_response.access_token, refresh_response.refresh_token)
        access_token = refresh_response.access_token
    return access_token


def password_authentication(auth: PasswordAuth):
    #Authenticate with workos
    workos_auth_response = workos.user_management.authenticate_with_password(
        email=auth.email,
        password=auth.password,
        ip_address=auth.ip_address,
        user_agent=auth.user_agent
    )
    
    decoded_token = decode_signed_token(workos_auth_response.access_token)
    expiration = decoded_token.get('exp')
    
    workos_session = WorkosSession(
        decoded_token.get('sid'),
        expiration,
        auth.ip_address,
        auth.user_agent,
        "",
        ""
        )
    workos_session.set_decrypted_access_token(workos_auth_response.access_token)
    workos_session.set_decrypted_refresh_token(workos_auth_response.refresh_token)
        
    # store the session in the database
    create_workos_session(workos_session)
    
    return workos_auth_response.access_token