# app/controllers/professors_controller.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.professor_service import get_all_professors
from app.models.response import ProfessorsResponse
from app.utils.logger import logger

router = APIRouter()


@router.get("/professors", response_model=ProfessorsResponse)
async def get_professors():
    """Endpoint mejorado con manejo robusto de errores"""
    try:
        logger.info("Iniciando obtención de datos de profesores")
        professors = get_all_professors()

        if not professors:
            logger.warning("No se encontraron datos de profesores")
            raise HTTPException(
                status_code=404,
                detail="No se encontraron datos de profesores"
            )

        logger.info(f"Datos obtenidos correctamente para {len(professors)} profesores")
        return {
            "professors": professors,
            "count": len(professors)
        }

    except HTTPException:
        raise
    except requests.RequestException as e:
        logger.error(f"Error de red al obtener datos: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Servicio temporalmente no disponible"
        )
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )