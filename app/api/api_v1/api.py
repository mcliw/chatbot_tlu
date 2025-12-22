from fastapi import APIRouter
from app.routers import auth
from app.api.api_v1.routers import chat, users, students

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])