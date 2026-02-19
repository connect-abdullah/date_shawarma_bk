import json
import hashlib
from time import time
from typing import Any, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)

# {cache_key: (data, timestamp)} - cache_key is a string
_cache: dict[str,tuple[Any, float]] = {}
DEFAULT_TTL = 900 # 15 minutes


def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a unique cache key from prefix and parameters."""
    # Sort keys for consistent hashing
    params_str = json.dumps(kwargs, sort_keys=True, default=str)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()
    return f"{prefix}:{params_hash}"

def get_cache(key:tuple) -> Any | None:
    if not key in _cache:
        return None
    value, expiry = _cache[key]
    if time() > expiry:
        del _cache[key]
        return None
    return value

def set_cache(key:tuple, value:Any, ttl: int = DEFAULT_TTL) -> None:
    _cache[key] = (value, time() + ttl)
    logger.debug(f"Cached data for key: {key}")


def invalidate_cache(prefix: Optional[str] = None) -> None:
    """Invalidate cache entries. If prefix is provided, only invalidate matching keys."""
    if prefix:
        keys_to_remove = [k for k in _cache.keys() if k.startswith(prefix)]
        for key in keys_to_remove:
            del _cache[key]
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries with prefix: {prefix}")
    else:
        _cache.clear()
        logger.info("Cleared all cache entries")
        
def get_cache_stats() -> dict:
    """Get cache statistics."""
    current_time = time.time()
    active_entries = 0
    expired_entries = 0
    
    for key, (_, cached_time) in _cache.items():
        if current_time - cached_time < DEFAULT_TTL:
            active_entries += 1
        else:
            expired_entries += 1
    
    return {
        "total_entries": len(_cache),
        "active_entries": active_entries,
        "expired_entries": expired_entries,
        "memory_usage_estimate": len(_cache) * 1024  # Rough estimate
    }