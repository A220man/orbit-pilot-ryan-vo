from fastapi import APIRouter

from app.api.v1 import audits

api_router = APIRouter()
api_router.include_router(audits.router, prefix="/api/v1")