from auth.apiv1.handler import router as auth_router
from fastapi import APIRouter
from health.apiv1.handler import router as health_router
from uploader.apiv1.handler import router as uploader_router
from user.apiv1.handler import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(health_router, tags=["Health"], prefix="/health")
api_router.include_router(user_router, tags=["User"], prefix="/user")
api_router.include_router(uploader_router, tags=["Uploader"], prefix="/uploader")
