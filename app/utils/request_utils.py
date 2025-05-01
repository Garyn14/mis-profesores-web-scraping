import requests
from typing import Optional
from app.core.config import settings
from app.core.logger import logger

def safe_request(url: str, retries: int = 3) -> Optional[requests.Response]:
    """Wrapper para requests con manejo de errores."""
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": settings.USER_AGENT},
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                import time
                time.sleep((attempt + 1) * 1)  # Backoff exponencial
    return None