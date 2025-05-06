"""Business logic for professor data"""
from typing import List
from app.cache.cache_manager import cache_response
from app.services.scraping_service import scrape_professors
from app.models.professor import Professor

UNIVERSITY_URL = "https://peru.misprofesores.com/escuelas/Universidad-Nacional-de-San-Marcos_1135"

@cache_response(expiration=3600)  # Cache for 1 hour
def get_all_professors() -> List[Professor]:
    """Get all professors with their evaluation data"""
    raw_professors = scrape_professors(UNIVERSITY_URL)
    return [Professor(**prof) for prof in raw_professors]