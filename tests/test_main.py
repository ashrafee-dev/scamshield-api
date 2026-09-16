from unittest.mock import MagicMock

import pytest


EXPECTED_UNSUPPORTED_AUDIO_ERROR = (
    "Unsupported audio content type. "
    "Accepted formats: MP3, M4A, MP4, WAV, WebM, OGG, FLAC."
)


def test_email_check(client, mocker):
    mocker.patch(
        "app.api.analyze.get_assessment",
        return_value={
            "label": "spam",
            "score": 90,
            "certainty": "high",
            "reason": "Suspicious request",
        },
    )
    response = client.post(
        "/email",
        json={
            "sender": "fraud420@gmail.com",
            "body": "Looking for Loans? Give your Bank Crendentials and get it within an hour",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert "label" in result
    assert "score" in result
    assert "certainty" in result
    assert "reason" in result


def test_http_unsupported_audio_error(client):
    response = client.post(
        "/audio",
        files={"file": ("invalid.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json() == {
        "detail": {"error": EXPECTED_UNSUPPORTED_AUDIO_ERROR}
    }


def test_websocket_unsupported_audio_error(client):
    with client.websocket_connect("/ws") as websocket:
        websocket.send_bytes(b"not audio")
        response = websocket.receive_json()

    assert response == {"error": EXPECTED_UNSUPPORTED_AUDIO_ERROR}


def test_audio_check(client, mocker):
    mocker.patch("app.api.analyze.audio_transcript", return_value="Sample audio text")
    mocker.patch(
        "app.api.analyze.get_assessment",
        return_value={
            "label": "safe",
            "score": 10,
            "certainty": "high",
            "reason": "No threat",
        },
    )
    with open("tests/test_audio.m4a", "rb") as audio:
        response = client.post("/audio", files={"file": audio})
    assert response.status_code == 200
    result = response.json()
    assert "label" in result
    assert "score" in result
    assert "certainty" in result
    assert "reason" in result


@pytest.fixture
def audio_bytes():
    with open("tests/test_audio.m4a", "rb") as audio:
        yield audio.read()


def test1(client, audio_bytes, mocker):
    mocker.patch("app.api.analyze.audio_transcript", return_value="Sample audio text")

    mock_assessment = MagicMock()
    mock_assessment.model_dump.return_value = {
        "label": "spam",
        "score": 80,
        "certainty": "high",
        "reason": "Phishing detection",
    }
    mocker.patch("app.api.analyze.get_assessment", return_value=mock_assessment)

    with client.websocket_connect("/ws") as websocket:
        websocket.send_bytes(audio_bytes)
        result = websocket.receive_json()
        assert "label" in result
        assert "score" in result
        assert "certainty" in result
        assert "reason" in result


def test_http_oversized_audio_error_includes_limit(client, monkeypatch):
    one_mb = 1024 * 1024
    monkeypatch.setattr("app.api.analyze.MAX_FILE_SIZE", one_mb)

    response = client.post(
        "/audio",
        files={"file": ("large.mp3", b"0" * (one_mb + 1), "audio/mpeg")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": {"error": "File too large. Max size is 1MB."}
    }


def test_websocket_oversized_audio_error_includes_limit(client, monkeypatch):
    one_mb = 1024 * 1024
    monkeypatch.setattr("app.api.analyze.MAX_FILE_SIZE", one_mb)

    with client.websocket_connect("/ws") as websocket:
        websocket.send_bytes(b"0" * (one_mb + 1))
        response = websocket.receive_json()

    assert response == {"error": "File too large. Max size is 1MB."}
