"""Cache management module"""
from functools import wraps
from datetime import datetime, timedelta
from app.config import get_settings

settings = get_settings()

class CacheManager:
    _cache = {}
    _timestamps = {}

    @classmethod
    def get(cls, key):
        """Retrieve item from cache if not expired"""
        if key in cls._cache:
            if datetime.now() < cls._timestamps[key]:
                return cls._cache[key]
            cls.clear(key)
        return None

    @classmethod
    def set(cls, key, value, expiration=None):
        """Store item in cache"""
        expiration = expiration or settings.cache_expiration
        cls._cache[key] = value
        cls._timestamps[key] = datetime.now() + timedelta(seconds=expiration)

    @classmethod
    def clear(cls, key=None):
        """Clear cache item or entire cache"""
        if key:
            cls._cache.pop(key, None)
            cls._timestamps.pop(key, None)
        else:
            cls._cache.clear()
            cls._timestamps.clear()

def cache_response(expiration=None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = CacheManager.get(cache_key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, expiration)
            return result
        return wrapper
    return decorator