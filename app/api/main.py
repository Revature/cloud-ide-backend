from fastapi import APIRouter
from app.api.routes import users, runners, machines, images, app_requests # import your new images route

api_router = APIRouter()
api_router.include_router(users.router, prefix="/api/v1/users", tags=["users"])
api_router.include_router(runners.router, prefix="/api/v1/runners", tags=["runners"])
# api_router.include_router(scripts.router, prefix="/api/v1/scripts", tags=["scripts"])
api_router.include_router(images.router, prefix="/api/v1/images", tags=["images"])
api_router.include_router(machines.router, prefix="/api/v1/machines", tags=["machines"])
api_router.include_router(app_requests.router, prefix="/api/v1/app_requests", tags=["app_requests"]) # include your new images route