"""FastAPI application entry point"""
from fastapi import FastAPI
from app.controllers import health_controller, professors_controller
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Microservice for professor evaluation data",
    version="1.0.0"
)

# Include routers
app.include_router(health_controller.router)
app.include_router(professors_controller.router, prefix="/api", tags=["Professors"])

@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    print(f"Starting {settings.app_name}...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down application...")