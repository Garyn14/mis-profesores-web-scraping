from typing import List, Dict
from cachetools import cached, TTLCache
from datetime import datetime
from app.api.schemas.profesores import ProfessorResponse
from app.core.config import settings
from app.utils.scraping_utils import scrape_university_professors
from app.utils.logger import logger

cache = TTLCache(maxsize=1, ttl=settings.CACHE_TTL)


@cached(cache)
async def get_raw_professors_data() -> List[Dict]:
    """Obtiene datos crudos con caché"""
    logger.debug("🔍 Buscando en caché o scraping nuevo...")
    try:
        data = await scrape_university_professors(settings.UNIVERSITY_URL)
        logger.info(f"📦 Datos crudos obtenidos: {len(data)} registros")
        return data
    except Exception as e:
        logger.error(f"❌ Fallo en get_raw_professors_data: {str(e)}")
        raise


async def get_professors_data() -> List[ProfessorResponse]:
    """Transforma datos y muestra progreso"""
    logger.info("🔄 Procesando datos...")
    start_time = datetime.now()

    try:
        raw_data = await get_raw_professors_data()
        if not raw_data:
            logger.warning("⚠️ No se obtuvieron datos para procesar")
            return []

        total = len(raw_data)
        processed = []

        # Mostrar barra de progreso solo una vez
        logger.info(f"📊 Procesando {total} profesores...")

        for i, prof in enumerate(raw_data, 1):
            try:
                processed.append(ProfessorResponse(**prof))
                # Mostrar progreso cada 20 registros o al final
                if i % 20 == 0 or i == total:
                    logger.progress(i, total, prefix="Progreso:", suffix=f"{i}/{total}")
            except Exception as e:
                logger.warning(f"⚠️ Error en registro {i}: {str(e)}")
                continue

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.success(f"✅ Procesamiento completado: {len(processed)}/{total} registros en {elapsed:.2f}s")
        return processed
    except Exception as e:
        logger.error(f"💥 Error crítico en get_professors_data: {str(e)}")
        raise


async def refresh_professors_data() -> List[ProfessorResponse]:
    """Limpia caché y recarga datos"""
    logger.warning("♻️ Limpiando caché y forzando rescrapeo...")
    try:
        cache.clear()
        return await get_professors_data()
    except Exception as e:
        logger.error(f"💥 Error al refrescar datos: {str(e)}")
        raise