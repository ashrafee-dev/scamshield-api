import sys
from unittest.mock import MagicMock

import fakeredis
import pytest
from fastapi.testclient import TestClient

# Prevent network calls from whisper model initialization during local execution
sys.modules["whisper"] = MagicMock()

from app.main import app  # pylint: disable=wrong-import-position


@pytest.fixture
def client():
    """Reusable FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    fake_server = fakeredis.FakeStrictRedis()
    mocker.patch("app.services.rate_limit.r", fake_server)
