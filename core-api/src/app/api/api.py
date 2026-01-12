from fastapi import APIRouter
from app.api.v1.endpoints import admin, chat

api_router = APIRouter()
# We will uncomment these as we implement them
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
# api_router.include_router(chat.router, tags=["chat"])
