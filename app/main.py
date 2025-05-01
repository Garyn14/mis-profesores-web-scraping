from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import profesores, universidades
from app.core.config import settings
from app.core.logger import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación"""
    # Código que se ejecuta al iniciar
    from app.services.scraping_service import get_professors_data
    await get_professors_data()
    yield  # La aplicación está ahora en estado de ejecución
    # Código que se ejecuta al cerrar (opcional)
    # Ejemplo: await close_database_connection()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,  # <-- Aquí registramos el manejador
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configuración inicial
    setup_logging()

    # Routers
    app.include_router(profesores.router)
    app.include_router(universidades.router)

    return app

app = create_application()

@app.get("/health", tags=["monitoring"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}