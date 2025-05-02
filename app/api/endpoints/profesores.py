from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.services.scraping_service import (
    get_professors_data,
    refresh_professors_data
)
from app.api.schemas.profesores import ProfessorResponse
from app.utils.logger import logger

router = APIRouter(prefix="/profesores", tags=["profesores"])

@router.get("/all", response_model=List[ProfessorResponse])
async def get_all_professors():
    """Obtiene todos los profesores (sin paginación)"""
    logger.info("📦 Solicitud GET /all - Iniciando...")
    try:
        data = await get_professors_data()
        logger.success(f"✅ GET /all completado | {len(data)} registros")
        return data
    except Exception as e:
        logger.error(f"❌ GET /all falló: {str(e)}")
        raise HTTPException(500, "Error interno al obtener datos")

@router.get("", response_model=List[ProfessorResponse])
async def list_professors(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Lista paginada de profesores"""
    logger.info(f"🔍 Solicitud GET / | Paginación: offset={offset}, limit={limit}")
    try:
        professors = await get_professors_data()
        result = professors[offset:offset + limit]
        logger.info(f"📊 Página {offset//limit + 1} entregada | {len(result)} items")
        return result
    except Exception as e:
        logger.error(f"❌ GET / falló: {str(e)}")
        raise HTTPException(500, "Error en paginación")

@router.post("/refresh")
async def refresh_data():
    """Forzar actualización de datos"""
    logger.warning("♻️ Solicitud POST /refresh - Reiniciando caché...")
    try:
        await refresh_professors_data()
        logger.success("🔄 Datos refrescados exitosamente")
        return {"status": "data refreshed"}
    except Exception as e:
        logger.error(f"💥 POST /refresh falló: {str(e)}")
        raise HTTPException(500, "Error al refrescar datos")