from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, pois, routes, progress, files

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pois.router, prefix="/pois", tags=["pois"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
