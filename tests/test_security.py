from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi import HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError
from starlette.websockets import WebSocketDisconnect

from app.api import analyze
from app.services.risk import AssessmentUnavailable


def test_unauthenticated_request_does_not_call_provider(client, mocker):
    provider = mocker.patch("app.api.analyze.get_assessment")
    client.headers.pop("authorization")
    response = client.post("/text", json={"body": "hello"})
    assert response.status_code == 401
    provider.assert_not_called()


def test_text_contract_and_legacy_email(client, mocker):
    expected = {"label": "Safe", "score": "Low", "certainty": 80, "reason": "No scam indicators"}
    mocker.patch("app.api.analyze.get_assessment", return_value=expected)
    for endpoint in ("/text", "/email"):
        response = client.post(endpoint, json={"body": "hello"})
        assert response.status_code == 200
        assert response.json() == expected


@pytest.mark.parametrize("body", ["", "   ", "a" * 10001])
def test_text_input_bounds(client, body):
    assert client.post("/text", json={"body": body}).status_code == 422


def test_upstream_failure_is_sanitized(client, mocker):
    mocker.patch("app.api.analyze.get_assessment", side_effect=AssessmentUnavailable("secret"))
    response = client.post("/text", json={"body": "hello"})
    assert response.status_code == 502
    assert "secret" not in response.text


def test_redis_outage_fails_closed(client, mocker):
    provider = mocker.patch("app.api.analyze.get_assessment")
    mocker.patch("app.services.rate_limit.r.pipeline", side_effect=RedisConnectionError("secret"))
    assert client.post("/text", json={"body": "hello"}).status_code == 503
    provider.assert_not_called()


def test_readiness_fails_when_redis_is_unavailable(client, mocker):
    mocker.patch("app.services.rate_limit.r.ping", side_effect=RedisConnectionError("secret"))
    assert client.get("/health").status_code == 200
    response = client.get("/ready")
    assert response.status_code == 503
    assert "secret" not in response.text


def test_http_rate_limit_has_retry_after(client, mocker):
    mocker.patch("app.services.auth.rate_limit.check_rate_limit", return_value=False)
    response = client.post("/text", json={"body": "hello"})
    assert response.status_code == 429
    assert int(response.headers["retry-after"]) > 0


def test_streamed_body_limit_without_content_length(client):
    def chunks():
        yield b'{"body":"'
        yield b"x" * 70000
        yield b'"}'
    assert client.post("/text", content=chunks()).status_code == 413


def test_declared_body_limit_rejects_before_analysis(client, mocker):
    provider = mocker.patch("app.api.analyze.get_assessment")
    assert client.post("/text", content=b"x" * 70000).status_code == 413
    provider.assert_not_called()


@pytest.mark.asyncio
async def test_chunked_multipart_limit_closes_partial_files(client, mocker):
    from starlette import formparsers  # pylint: disable=import-outside-toplevel
    opened = []
    original = formparsers.SpooledTemporaryFile

    def record_file(*args, **kwargs):
        # The parser owns this handle; the test verifies it closes on rejection.
        handle = original(*args, **kwargs)  # pylint: disable=consider-using-with
        opened.append(handle)
        return handle

    mocker.patch.object(formparsers, "SpooledTemporaryFile", side_effect=record_file)
    mocker.patch("app.middleware.MAX_FILE_SIZE", 1024)

    async def chunks():
        yield (b'--boundary\r\nContent-Disposition: form-data; name="file"; filename="x.wav"'
               b'\r\nContent-Type: audio/wav\r\n\r\n' + b"x" * 4096)
        yield b"x" * 70000
        yield b"\r\n--boundary--\r\n"

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=client.app), base_url="http://test",
    ) as requester:
        response = await requester.post(
            "/audio", content=chunks(), headers={
                "Authorization": client.headers["authorization"],
                "Content-Type": "multipart/form-data; boundary=boundary",
            },
        )
    assert response.status_code == 413
    assert opened and all(handle.closed for handle in opened)


def test_invalid_token_rejected_before_reading_body(client):
    response = client.post(
        "/audio", headers={"Authorization": "Bearer wrong", "Content-Length": "999999999"},
    )
    assert response.status_code == 401


def test_temp_audio_removed_and_slot_released_on_error(mocker):
    paths = []

    def fail(path):
        assert Path(path).exists()
        paths.append(path)
        raise RuntimeError("transcription failed")

    mocker.patch("app.api.analyze.audio_transcript", side_effect=fail)
    data = Path("tests/test_audio.m4a").read_bytes()
    for _ in range(2):
        with pytest.raises(RuntimeError):
            analyze.analyze_audio(data)
    assert all(not Path(path).parent.exists() for path in paths)


def test_audio_busy_rejects_instead_of_queuing():
    with analyze.audio_slot:
        with pytest.raises(HTTPException) as exc:
            analyze.analyze_audio(Path("tests/test_audio.m4a").read_bytes())
    assert exc.value.status_code == 503


def test_audio_read_is_bounded(mocker):
    upload = MagicMock()
    mocker.patch("app.api.analyze.analyze_audio")
    analyze.audio_check(upload)
    upload.file.read.assert_called_once_with(analyze.MAX_FILE_SIZE + 1)


def test_websocket_requires_authentication(client):
    client.headers.pop("authorization")
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws"):
            pytest.fail("Unauthenticated connection accepted")


def test_websocket_rejects_unapproved_origin(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws", headers={"Origin": "https://untrusted.example"}):
            pytest.fail("Unapproved origin accepted")


def test_websocket_text_frame_closes_cleanly(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("not audio")
        with pytest.raises(WebSocketDisconnect) as exc:
            websocket.receive_json()
    assert exc.value.code == 1003
