import time

import redis

from app.config import MAX_REQUEST_LIMIT, RATE_LIMIT_WINDOW

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def check_rate_limit(ip: str) -> bool:
    now = time.time()
    print(now)
    user = r.hgetall(ip)
    if user:
        if int(user["NUM_REQUESTS"]) <= 0:
            if RATE_LIMIT_WINDOW > now - float(user["LAST_REQUEST_TIME"]):
                return False
            else:
                r.hset(
                    ip,
                    mapping={
                        "NUM_REQUESTS": MAX_REQUEST_LIMIT,
                        "LAST_REQUEST_TIME": now,
                    },
                )
                r.hincrby(ip, "NUM_REQUESTS", -1)
            return True
    else:
        r.hset(
            ip,
            mapping={
                "NUM_REQUESTS": MAX_REQUEST_LIMIT,
                "LAST_REQUEST_TIME": now,
            },
        )
    r.hincrby(ip, "NUM_REQUESTS", -1)
    return True
