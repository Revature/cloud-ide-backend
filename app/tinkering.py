import os
from fastapi import APIRouter
from workos import WorkOSClient

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"), 
    client_id=os.getenv("WORKOS_CLIENT_ID")
)

router = APIRouter()

class PasseordAuth():
    email: str
    password: str
    
user_and_organization = workos.user_management.authenticate_with_password(
    email="test@revature.com",
    password='c[@~"L*2]El7WVrq',
    ip_address="192.0.2.1",
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
)

print(user_and_organization)
print(user_and_organization.user)
print(user_and_organization.user.id)
print(user_and_organization.user.first_name)
print(user_and_organization.user.last_name)
