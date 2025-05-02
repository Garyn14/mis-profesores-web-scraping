import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict, Optional
from app.core.config import settings
from app.utils.logger import logger
from app.utils.request_utils import safe_request


def replace_latin_chars(s: str) -> str:
    """Normaliza caracteres latinos"""
    translate = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N", "Ü": "U",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u"
    }
    return re.sub(r'[ÁÉÍÓÚÑÜáéíóúñü]', lambda match: translate[match.group(0)], s)


def clean_string_for_url(s: str) -> str:
    """Limpia formato para URL"""
    s = replace_latin_chars(s)
    s = re.sub(r'[^a-zA-Z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s.strip())
    return s.lower()


def extract_professors_data(soup: BeautifulSoup) -> Optional[List[Dict]]:
    """Extrae datos de profesores de la página"""
    logger.debug("🔎 Buscando datos de profesores en el HTML")
    for script in soup.find_all('script'):
        if script.string and 'var dataSet =' in script.string:
            logger.debug("📦 Script con dataSet encontrado")
            match = re.search(r'var dataSet\s*=\s*(\[\{.*?}]);', script.string, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    logger.info(f"📊 Datos crudos obtenidos: {len(data)} registros")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error al parsear JSON: {e}")
    logger.warning("⚠️ No se encontró el dataSet en la página")
    return None


async def scrape_university_professors(university_url: str = settings.UNIVERSITY_URL) -> List[Dict]:
    """Realiza el scraping de los profesores con seguimiento de progreso"""
    logger.info(f"🚀 Iniciando scraping para: {university_url}")
    start_time = time.time()

    try:
        # Paso 1: Obtener datos básicos
        logger.info("📥 Obteniendo página principal...")
        response = safe_request(university_url)
        if not response:
            logger.error("❌ No se pudo obtener la página inicial")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        raw_data = extract_professors_data(soup)
        if not raw_data:
            logger.error("❌ No se encontraron datos de profesores")
            return []

        # Paso 2: Procesar datos básicos
        total_professors = len(raw_data)
        professors = []

        logger.info(f"🔧 Transformando {total_professors} registros...")

        for i, prof in enumerate(raw_data, 1):
            try:
                professor_data = {
                    'id': prof.get('i', ''),
                    'name': f"{prof.get('n', '')} {prof.get('a', '')}",
                    'faculty': prof.get('d', ''),
                    'ratings_count': int(prof.get('m', 0)),
                    'average_rating': float(prof.get('c', 0)) if str(prof.get('c', '')).replace('.', '',
                                                                                                1).isdigit() else 0.0,
                    'profile_url': f"{settings.BASE_URL}/profesores/"
                                   f"{clean_string_for_url(prof.get('n', ''))}-"
                                   f"{clean_string_for_url(prof.get('a', ''))}_"
                                   f"{prof.get('i', '')}",
                    'tags': [],
                    'stats': {},
                    'comments': []
                }
                professors.append(professor_data)

                # Mostrar progreso cada 25 registros o al final
                if i % 25 == 0 or i == total_professors:
                    logger.progress(i, total_professors, prefix="Scraping:", suffix=f"{i}/{total_professors}")

            except Exception as e:
                logger.warning(f"⚠️ Error procesando profesor {i}: {e}")
                continue

        elapsed_time = time.time() - start_time
        logger.success(f"🎉 Scraping completado en {elapsed_time:.2f} segundos | Total: {len(professors)} registros")

        return professors

    except Exception as e:
        logger.error(f"💥 Error crítico durante el scraping: {str(e)}")
        return []
