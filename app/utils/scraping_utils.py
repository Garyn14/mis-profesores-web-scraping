import requests
from bs4 import BeautifulSoup
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.logger import logger


def replace_latin_chars(s: str) -> str:
    """Normaliza caracteres especiales del español."""
    translate = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N", "Ü": "U",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u"
    }
    return re.sub(r'[ÁÉÍÓÚÑÜáéíóúñü]', lambda match: translate[match.group(0)], s)


def clean_string_for_url(s: str) -> str:
    """Limpia y formatea strings para URLs."""
    s = replace_latin_chars(s)
    s = re.sub(r'[^a-zA-Z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s.strip())
    return s.lower()


def safe_request(url: str, retries: int = 3) -> Optional[requests.Response]:
    """Maneja requests con reintentos y delays."""
    for attempt in range(retries):
        try:
            logger.debug(f"🔍 Intentando request a {url} (intento {attempt + 1}/{retries})")
            response = requests.get(url, headers=settings.REQUEST_HEADERS)
            response.raise_for_status()
            logger.debug("✅ Request exitoso")
            return response
        except requests.RequestException as e:
            logger.warning(f"⚠️ Request fallido (intento {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 1)
    logger.error(f"❌ Todos los intentos fallaron para {url}")
    return None


def extract_professors_data(soup: BeautifulSoup) -> Optional[List[Dict]]:
    """Extrae el dataset de profesores del script JavaScript."""
    logger.info("🔎 Buscando datos de profesores en el HTML")
    for script in soup.find_all('script'):
        if script.string and 'var dataSet =' in script.string:
            logger.debug("📦 Script con dataSet encontrado")
            match = re.search(r'var dataSet\s*=\s*(\[\{.*?\}\]);', script.string, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    logger.info(f"📊 Datos crudos obtenidos: {len(data)} registros")
                    return data
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error al parsear JSON: {e}")
    logger.warning("⚠️ No se encontró el dataSet en la página")
    return None


def scrape_university_professors(university_url: str = settings.UNIVERSITY_URL) -> List[Dict]:
    """Función principal de scraping con logging detallado."""
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
        logger.info("🔄 Procesando datos de profesores...")
        professors = []
        total_professors = len(raw_data)

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

                # Log cada 10 profesores o al final
                if i % 10 == 0 or i == total_professors:
                    logger.info(f"⏳ Progreso: {i}/{total_professors} profesores procesados")

            except Exception as e:
                logger.error(f"❌ Error procesando profesor {i}: {e}")
                continue

        elapsed_time = time.time() - start_time
        logger.info(f"✅ Scraping completado en {elapsed_time:.2f} segundos")
        logger.info(f"📈 Total de profesores obtenidos: {len(professors)}")

        return professors

    except Exception as e:
        logger.error(f"💥 Error crítico durante el scraping: {str(e)}")
        return []