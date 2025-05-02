import requests
from typing import Optional
from app.core.config import settings


# Make 3 attempts if the request fails
def safe_request(url: str, retries: int = 3) -> Optional[requests.Response]:
    """wrap each request to management errors"""
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": settings.REQUEST_HEADERS["User-Agent"]},
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                import time
                time.sleep((attempt + 1) * 1)
    return None
