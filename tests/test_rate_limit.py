from unittest.mock import patch

from app.config import MAX_REQUEST_LIMIT, RATE_LIMIT_WINDOW
from app.services import rate_limit as rate_limit_mod


def _user(num_requests: int, last_request_time: float) -> dict:
    return {
        "NUM_REQUESTS": str(num_requests),
        "LAST_REQUEST_TIME": str(last_request_time),
    }


@patch("app.services.rate_limit.time.time", return_value=1_000.0)
@patch("app.services.rate_limit.r")
def test_exhausted_quota_blocked_inside_configured_window(mock_redis, _mock_time):
    mock_redis.hgetall.return_value = _user(0, 1_000.0 - (RATE_LIMIT_WINDOW - 1))

    allowed = rate_limit_mod.check_rate_limit("203.0.113.10")

    assert allowed is False
    mock_redis.hset.assert_not_called()


@patch("app.services.rate_limit.time.time", return_value=1_000.0)
@patch("app.services.rate_limit.r")
def test_exhausted_quota_resets_after_configured_window(mock_redis, mock_time):
    mock_redis.hgetall.return_value = _user(0, 1_000.0 - RATE_LIMIT_WINDOW)

    allowed = rate_limit_mod.check_rate_limit("203.0.113.11")

    assert allowed is True
    mock_redis.hset.assert_called_once_with(
        "203.0.113.11",
        mapping={
            "NUM_REQUESTS": MAX_REQUEST_LIMIT,
            "LAST_REQUEST_TIME": mock_time.return_value,
        },
    )


@patch("app.services.rate_limit.time.time", return_value=1_000.0)
@patch("app.services.rate_limit.r")
def test_configured_window_is_honored(mock_redis, mock_time, monkeypatch):
    monkeypatch.setattr(rate_limit_mod, "RATE_LIMIT_WINDOW", 30)

    # 31 seconds ago is outside a 30s window, so the quota should reset.
    mock_redis.hgetall.return_value = _user(0, 1_000.0 - 31)

    assert rate_limit_mod.check_rate_limit("203.0.113.12") is True

    # 29 seconds ago is still inside a 30s window, so the request is blocked.
    mock_redis.hgetall.return_value = _user(0, 1_000.0 - 29)
    mock_redis.hset.reset_mock()

    assert rate_limit_mod.check_rate_limit("203.0.113.12") is False
    mock_redis.hset.assert_not_called()
