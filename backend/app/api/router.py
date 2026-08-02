from fastapi import APIRouter
from app.api.endpoints import health, parse, context

api_router = APIRouter()
api_router.include_router(health.router, prefix="/system", tags=["System & Health"])
api_router.include_router(parse.router, prefix="/parser", tags=["Command Parser Engine"])
api_router.include_router(context.router, prefix="/context", tags=["System Context Engine"])
