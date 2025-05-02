from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import profesores
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicación...")
    yield
    logger.info("🛑 Aplicación cerrada")

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
    )

    # CORS configuration
    origins = [settings.ALLOWED_ORIGINS] if isinstance(settings.ALLOWED_ORIGINS, str) else settings.ALLOWED_ORIGINS

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        allow_credentials=True,
        expose_headers=["*"]
    )

    # Routers
    app.include_router(profesores.router)

    # Middleware para logging
    @app.middleware("http")
    async def log_requests(request, call_next):
        logger.info(f"🌐 Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"📡 Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"💥 Error en request: {str(e)}")
            raise

    return app

app = create_application()

@app.get("/health", tags=["monitoring"])
async def health_check():
    logger.info("🩺 Health check ejecutándose")
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "allowed_origin": settings.ALLOWED_ORIGINS,
    }