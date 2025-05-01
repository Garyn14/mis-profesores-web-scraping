from datetime import datetime
from typing import List, Optional, Dict
from cachetools import cached, TTLCache
from app.utils.scraping_utils import scrape_university_professors
from app.api.schemas.profesores import ProfessorResponse, ProfessorDetail
from app.core.config import settings

# Cache de 1 hora (configurable en .env)
cache = TTLCache(maxsize=1, ttl=settings.CACHE_TTL)

@cached(cache)
async def get_raw_professors_data() -> List[Dict]:
    """Obtiene datos crudos con caché"""
    return scrape_university_professors(settings.UNIVERSITY_URL)

async def get_professors_data() -> List[ProfessorResponse]:
    """Obtiene datos procesados de todos los profesores"""
    raw_data = await get_raw_professors_data()
    return [ProfessorResponse(**prof) for prof in raw_data]

async def get_professor_by_id(professor_id: str) -> Optional[ProfessorDetail]:
    """Obtiene un profesor específico con todos sus detalles"""
    raw_data = await get_raw_professors_data()
    for prof in raw_data:
        if prof["id"] == professor_id:
            return ProfessorDetail(
                **prof,
                last_updated=datetime.now()
            )
    return None

async def refresh_professors_data() -> List[ProfessorResponse]:
    """Fuerza la actualización de los datos (limpia la caché)"""
    cache.clear()
    return await get_professors_data()