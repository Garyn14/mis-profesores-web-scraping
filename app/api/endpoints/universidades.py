from fastapi import APIRouter
from app.api.schemas.universidades import UniversityResponse

router = APIRouter(prefix="/universidades", tags=["universidades"])

@router.get("/", response_model=UniversityResponse)
async def get_university_info():
    """Obtiene información de la universidad actual"""
    return {
        "name": "Universidad Nacional de San Marcos",
        "url": "https://peru.misprofesores.com/escuelas/Universidad-Nacional-de-San-Marcos_1135",
        "professor_count": 0  # Se actualizará dinámicamente
    }