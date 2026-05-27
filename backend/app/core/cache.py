import redis.asyncio as redis
from ..config import settings
import functools
import json
from fastapi import Request, Response

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache(expire: int = 300):
    """
    Simple caching decorator using Redis.
    Caches JSON responses for GET endpoints based on the request URL.
    Note: The decorated endpoint MUST accept a `request: Request` parameter.
    """
    def decorator(func):
        import inspect
        sig = inspect.signature(func)
        has_request = "request" in sig.parameters

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                # Fallback: if no request is passed, just call the original function
                return await func(*args, **kwargs)

            if request.method != "GET":
                return await func(*args, **kwargs)

            cache_key = f"cache:{request.url.path}?{request.url.query}"
            
            try:
                cached_val = await redis_client.get(cache_key)
                if cached_val:
                    return json.loads(cached_val)
            except Exception:
                # If Redis is unavailable, bypass cache
                return await func(*args, **kwargs)

            result = await func(*args, **kwargs)
            
            # Serialize the dict/list result to JSON and store it
            if isinstance(result, (dict, list)):
                try:
                    await redis_client.setex(cache_key, expire, json.dumps(result))
                except Exception:
                    pass
            
            return result
        return wrapper
    return decorator
