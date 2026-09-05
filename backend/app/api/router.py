from fastapi import APIRouter

from app.api.routes import datasets, health, organizations

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(datasets.router, prefix="/organizations", tags=["datasets"])
