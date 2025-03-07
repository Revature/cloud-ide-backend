import os
import jwt
import json
import httpx
from datetime import time
from sqlmodel import Session
from workos import WorkOSClient, exceptions
from fastapi import APIRouter, Depends, Request, Response
from app.models.workos_session import WorkosSession, create_workos_session

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"), 
    client_id=os.getenv("WORKOS_CLIENT_ID")
)

router = APIRouter()

class PasswordAuth:
    email: str
    password: str
    # def __init__(self, email, password):
    #     self.email = email
    #     self.password = password
    
@router.post("/machine_auth")
def machine_auth(request: Request, passwordAuth: PasswordAuth, response: Response):
    
    ip_address = request.client.host
    user_agent = request.headers.get('User-Agent')
    
    try:
        #Authenticate with workos
        workos_auth_response = workos.user_management.authenticate_with_password(
            email=passwordAuth.email,
            password=passwordAuth.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        #get the signing keys
        #TODO: We should cache these keys until the parsing fails to match a kid, then refresh it.
        response = httpx.get(workos.user_management.get_jwks_url())
        keys = json.loads(response.text)
        
    except exceptions.BadRequestException:
        response.status_code = 401
        return '{"error": "Unauthorized: bad credentials"}'
    except:
        response.status_code = 500
        return '{"error": "Internal Server Error"}'
    
    # parse the signing keys - fix this up later, logic could be better
    public_keys = {}
    for jwk in keys['keys']:
        kid = jwk['kid']
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        
    kid = jwt.get_unverified_header(workos_auth_response.access_token)['kid']
    key = public_keys[kid]
    
    # decode the signed access token
    decoded = jwt.decode(workos_auth_response.access_token, key=key, algorithms=['RS256'])
    exp = decoded.get('exp')

    workos_session = WorkosSession(
        decoded.get('sid'),
        exp,
        ip_address,
        user_agent,
        "",
        ""
        )
    workos_session.set_decrypted_access_token(workos_auth_response.access_token)
    workos_session.set_decrypted_refresh_token(workos_auth_response.refresh_token)
        
    # store the session in the database
    create_workos_session(workos_session)
    
    response.headers["Access-Token"] = workos_auth_response.access_token
    response.status_code = 200
    return '{"status": 200}'
    

    
    