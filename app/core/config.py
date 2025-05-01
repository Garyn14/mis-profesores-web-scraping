from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "mis-profesores-scraping"
    VERSION: str = "1.0.0"
    UNIVERSITY_URL: str
    CACHE_TTL: int = 3600
    API_KEY: Optional[str] = None
    DEBUG: bool = False
    REQUEST_HEADERS: dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    BASE_URL: str = "https://peru.misprofesores.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()