from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, professionals, services, chat, admin

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(professionals.router)
api_router.include_router(services.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router)
