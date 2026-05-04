import asyncio
from functools import wraps
from openai import AuthenticationError
import logging
# ===========================================================
# Utility functions mostly for connections and other services 
# ===========================================================

def async_retry(retries=3, delay=4):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, AuthenticationError):
                        raise
                    
                    attempts += 1
                    if attempts >= retries:
                        logging.error(f"All {retries} attempts to connect failed:  [{e}]")
                        raise
                    await asyncio.sleep(delay * attempts)
        return wrapper
    return decorator
