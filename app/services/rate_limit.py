import redis

from app.config import MAX_REQUEST_LIMIT, RATE_LIMIT_WINDOW, REDIS_URL

r = redis.Redis.from_url(
    REDIS_URL, decode_responses=True, socket_connect_timeout=2, socket_timeout=2,
)


def check_rate_limit(identity: str) -> bool:
    """Atomically count requests in a fixed window, including concurrent callers."""
    key = f"scamshield:rate:{identity}"
    with r.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        # Redis 7+: only the first request sets the expiry; later requests cannot extend it.
        pipe.expire(key, RATE_LIMIT_WINDOW, nx=True)
        count, _ = pipe.execute()
    return count <= MAX_REQUEST_LIMIT
