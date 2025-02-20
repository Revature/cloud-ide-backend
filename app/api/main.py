from fastapi import APIRouter
from app.api.routes import users, runners, machines, images  # import your new images route

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(runners.router, prefix="/runners", tags=["runners"])
# api_router.include_router(scripts.router, prefix="/scripts", tags=["scripts"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])