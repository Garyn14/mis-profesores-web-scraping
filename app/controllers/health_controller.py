"""Health check controller"""
from fastapi import APIRouter
from app.models.response import HealthCheck

router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }