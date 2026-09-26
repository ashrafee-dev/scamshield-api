from concurrent.futures import ThreadPoolExecutor

from app.config import MAX_REQUEST_LIMIT, RATE_LIMIT_WINDOW
from app.services import rate_limit


def test_concurrent_requests_cannot_exceed_quota():
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(rate_limit.check_rate_limit, ["same-user"] * 40))
    assert sum(results) == MAX_REQUEST_LIMIT
    assert 0 < rate_limit.r.ttl("scamshield:rate:same-user") <= RATE_LIMIT_WINDOW


def test_later_requests_do_not_extend_window():
    rate_limit.check_rate_limit("user")
    rate_limit.r.expire("scamshield:rate:user", 10)
    rate_limit.check_rate_limit("user")
    assert 0 < rate_limit.r.ttl("scamshield:rate:user") <= 10


def test_expired_window_resets_quota():
    for _ in range(MAX_REQUEST_LIMIT):
        assert rate_limit.check_rate_limit("user")
    assert not rate_limit.check_rate_limit("user")
    rate_limit.r.expire("scamshield:rate:user", 0)
    assert rate_limit.check_rate_limit("user")


def test_principals_have_independent_quotas():
    for _ in range(MAX_REQUEST_LIMIT):
        rate_limit.check_rate_limit("first")
    assert not rate_limit.check_rate_limit("first")
    assert rate_limit.check_rate_limit("second")
