"""
Utilidades de caché Redis para la API de Gaming Hub.
"""

import json
import redis
from typing import Any, Optional
from functools import wraps
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
import hashlib
import time
import inspect


class RedisCache:
    """Redis cache manager for API endpoints."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.default_ttl = 300  # 5 minutes default

    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            self.redis_client.ping()
            return True
        except redis.ConnectionError:
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

    def get_or_set(self, key: str, func, ttl: int = None):
        """Get from cache or set if not exists."""
        cached = self.get(key)
        if cached is not None:
            return cached

        result = func()
        self.set(key, result, ttl)
        return result


# Instancia global de caché
cache = RedisCache()


def cached_endpoint(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching FastAPI endpoints.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave de caché a partir del nombre de la función y argumentos
            func_name = f"{key_prefix}:{func.__name__}"
            arg_str = str(sorted(kwargs.items()))
            cache_key = f"{func_name}:{hashlib.md5(arg_str.encode()).hexdigest()}"

            # Intentar obtener primero del caché
            if cache.is_connected():
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # Ejecutar función (manejar sincrónico/async)
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # llamar de forma sincrónica
                result = func(*args, **kwargs)

            # Preparar valor para el caché
            cache_value = jsonable_encoder(result)
            # Guardar el resultado en el caché
            if cache.is_connected():
                cache.set(cache_key, cache_value, ttl)

            # ¿Devolver original o codificado? FastAPI puede manejar dicts/listas
            return cache_value
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """Invalidate cache keys matching pattern."""
    if cache.is_connected():
        return cache.clear_pattern(pattern)
    return 0