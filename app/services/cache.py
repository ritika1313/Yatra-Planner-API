import time

_cache: dict[str, dict] = {}

def get_cache(Key: str) -> dict | None:
    if Key not in _cache:
        return None

    entry = _cache[Key]
    if time.time() - entry["timestamp"] > entry["ttl"]:
        del _cache[Key]
        return None
    return entry["data"]


def set_cache(Key: str, data: dict, ttl: int) -> None:
    _cache[Key] = {
        "data": data,
        "timestamp": time.time(),
        "ttl": ttl,
    }

def clear_cache() -> None:
    _cache.clear()