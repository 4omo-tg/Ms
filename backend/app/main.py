from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for Moscow Chrono Walker - Historical Exploration Game",
    version="0.1.0"
)

# Ensure uploads dir exists
if not os.path.exists("app/uploads"):
    os.makedirs("app/uploads")

app.mount("/static", StaticFiles(directory="app/uploads"), name="static")

from app.web import admin
app.include_router(admin.router, prefix="/admin", tags=["admin"])

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Moscow Chrono Walker API"}
