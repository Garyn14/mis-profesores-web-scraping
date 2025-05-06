"""Application configuration settings"""
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Professor Evaluation Service"
    cache_expiration: int = 3600  # 1 hour in seconds
    debug: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()