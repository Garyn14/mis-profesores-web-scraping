"""Web scraping service implementation"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests

# Configuration
BASE_URL = 'https://peru.misprofesores.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
MAX_RETRIES = 3
REQUEST_DELAY = 1

def safe_request(url: str) -> Optional[requests.Response]:
    """Make HTTP request with error handling and timeout"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=(3.05, 27)  # Connect timeout, read timeout
            )
            response.raise_for_status()
            return response
        except requests.Timeout:
            logger.warning(f"Timeout en intento {attempt + 1} para {url}")
        except requests.RequestException as e:
            logger.warning(f"Error en intento {attempt + 1} para {url}: {str(e)}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(REQUEST_DELAY * (attempt + 1))

    logger.error(f"Todos los intentos fallaron para {url}")
    return None

def extract_professors_data(soup: BeautifulSoup) -> Optional[List[Dict]]:
    """Extract professors dataset from JavaScript"""
    for script in soup.find_all('script'):
        if script.string and 'var dataSet =' in script.string:
            match = re.search(r'var dataSet\s*=\s*(\[\{.*?\}\]);', script.string, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {str(e)}")
    return None

# app/services/scraping_service.py (actualización)
def process_professor_data(raw_data: List[Dict]) -> List[Dict]:
    """Procesa datos crudos - ahora incluye comments_url"""
    processed = []
    for prof in raw_data:
        first_name = clean_string_for_url(prof.get('n', ''))
        last_name = clean_string_for_url(prof.get('a', ''))
        prof_id = prof.get('i', '')

        base_url = f"{BASE_URL}/profesores/{first_name}-{last_name}_{prof_id}"

        processed.append({
            'id': prof_id,
            'name': f"{prof.get('n', '')} {prof.get('a', '')}",
            'faculty': prof.get('d', ''),
            'ratings_count': safe_int(prof.get('m')),
            'average_rating': safe_float(prof.get('c')),
            'profile_url': base_url,
            'comments_url': f"{base_url}/comentarios",  # Nueva URL
            'tags': [],
            'stats': {},
            'comments': []
        })
    return processed

def scrape_professor_details(professor: Dict) -> Dict:
    """Scrape additional details for a professor"""
    if professor['ratings_count'] == 0:
        return professor

    response = safe_request(professor['profile_url'])
    if not response:
        return professor

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract stats
    stats = {}
    for metric in ['takeAgain', 'difficulty']:
        div = soup.find('div', class_=lambda c: c and metric in c)
        if div:
            grade = div.find('div', class_='grade')
            if grade:
                stats[metric] = grade.get_text(strip=True)

    # Extract tags
    tag_box = soup.find('div', class_='tag-box')
    if tag_box:
        tags = [tag.get_text(strip=True) for tag in
                tag_box.find_all('span', class_='tag-box-choosetags')]
        professor['tags'] = tags

    professor['stats'] = stats
    return professor

def scrape_professor_comments(professor: Dict) -> Dict:
    """Scrape comments for a professor"""
    if professor['ratings_count'] == 0:
        return professor

    pages = (professor['ratings_count'] + 4) // 5  # 5 comments per page
    comments = []

    for page in range(1, pages + 1):
        url = f"{professor['profile_url']}?pag={page}"
        response = safe_request(url)
        if not response:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='tftable')
        if not table:
            continue

        for row in table.find_all('tr')[1:]:  # Skip header
            comment = {
                'date': get_text_or_default(row, 'div.date'),
                'summary': get_text_or_default(row, 'span.rating-type'),
                'overall_quality': get_text_or_default(row, 'span.score', 0),
                'difficulty': get_text_or_default(row, 'span.score', 1),
                'course': get_text_or_default(row, 'span.class, span.name, span.response'),
                'grade': clean_grade(get_text_or_default(row, 'span.grade')),
                'text': get_text_or_default(row, 'p.commentsParagraph')
            }
            comments.append(comment)

        time.sleep(REQUEST_DELAY)

    professor['comments'] = comments
    return professor

# app/services/scraping_service.py (con nuevo logger)
from app.utils.logger import logger, progress_logger

def scrape_professors(university_url: str) -> List[Dict]:
    """Función principal con concurrencia corregida"""
    try:
        progress_logger.start_stage("Scraping professors", 3)

        # Paso 1: Obtener lista de profesores
        progress_logger.start_stage("Fetching professor list")
        response = safe_request(university_url)
        if not response:
            logger.error("❌ Failed to get initial page")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        raw_data = extract_professors_data(soup)
        professors = process_professor_data(raw_data)
        progress_logger.end_stage(f"Found {len(professors)} professors")

        # Paso 2: Obtener detalles con ThreadPoolExecutor
        progress_logger.start_stage("Fetching professor details", len(professors))
        detailed_professors = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Usar el as_completed de concurrent.futures
            futures = [executor.submit(scrape_professor_details, prof) for prof in professors]

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result()
                    detailed_professors.append(result)
                    # Mostrar progreso cada 20 profesores o al final
                    if i % 20 == 0 or i == len(professors):
                        progress_logger.progress(i, len(professors),
                                                 f"Last: {result.get('name', 'unknown')}")
                except Exception as e:
                    logger.error(f"⚠️ Error processing professor: {str(e)}")

        progress_logger.end_stage(f"Processed {len(detailed_professors)} professors")

        # Paso 3: Obtener comentarios (sin concurrencia para evitar bloqueos)
        progress_logger.start_stage("Fetching comments", len(detailed_professors))
        final_results = []

        for i, professor in enumerate(detailed_professors, 1):
            try:
                final_results.append(scrape_professor_comments(professor))
                # Mostrar progreso cada 10 profesores o al final
                if i % 10 == 0 or i == len(detailed_professors):
                    progress_logger.progress(i, len(detailed_professors),
                                             f"Current: {professor['name']}")
            except Exception as e:
                logger.error(f"⚠️ Error in {professor['name']}: {str(e)}")
                final_results.append(professor)

        progress_logger.end_stage(f"Fetched {sum(len(p['comments']) for p in final_results)} comments")

        logger.info(f"✨ Scraping completed successfully")
        return final_results

    except Exception as e:
        logger.error(f"🔥 Critical error: {str(e)}", exc_info=True)
        return []

# Helper functions (same as in original script)
def safe_int(value) -> int:
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

def safe_float(value) -> float:
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def get_text_or_default(element, selector: str, index: int = None) -> str:
    if element is None:
        return 'N/A'
    found = element.select(selector)
    if not found:
        return 'N/A'
    if index is not None:
        return found[index].get_text(strip=True) if len(found) > index else 'N/A'
    return found[0].get_text(strip=True)

def clean_grade(grade: str) -> str:
    return grade.replace('Calificación Recibida: ', '') if grade != 'N/A' else grade

def clean_string_for_url(s: str) -> str:
    translate = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N", "Ü": "U",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u"
    }
    s = re.sub(r'[ÁÉÍÓÚÑÜáéíóúñü]', lambda match: translate[match.group(0)], s)
    s = re.sub(r'[^a-zA-Z0-9\s-]', '', s)
    s = re.sub(r'[\s-]+', '-', s.strip())
    return s.lower()