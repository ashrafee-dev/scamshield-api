"""Run inside the built API container against its running server; no paid calls."""
import io
import json
import os
import tempfile
import urllib.error
import urllib.request
import wave
from unittest.mock import patch

import whisper
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import connect

assert "turbo" in whisper.available_models()
assert os.access(os.path.expanduser("~/.cache"), os.W_OK)


def request(path, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"http://127.0.0.1:8000{path}", data=body, headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


assert request("/ready")[0] == 200
assert request("/text", b'{"body":"hello"}')[0] == 401
token_value = os.environ["SCAMSHIELD_API_KEYS"].split(",")[0]
assert request("/text", b'{"body":""}', token_value)[0] == 422

# Real Redis, bounded quota, no model calls: invalid audio is rejected before inference.
for _ in range(int(os.getenv("MAX_REQUEST_LIMIT", "10"))):
    request("/audio", b"{}", token_value)
assert request("/audio", b"{}", token_value)[0] == 429

with connect(
    "ws://127.0.0.1:8000/ws", additional_headers={"Authorization": f"Bearer {token_value}"},
) as websocket:
    websocket.send(b"not audio")
    assert json.loads(websocket.recv())["error"] == "Rate limit exceeded"
    try:
        websocket.recv()
    except ConnectionClosed as exc:
        assert exc.rcvd.code == 1013
    else:
        raise AssertionError("Rate-limited WebSocket stayed open")

# Decode a real WAV with the container's FFmpeg; stub only Whisper inference.
from app.services.transcription import audio_transcript  # pylint: disable=wrong-import-position

buffer = io.BytesIO()
with wave.Wave_write(buffer) as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b"\0\0" * 16000)
with tempfile.NamedTemporaryFile(suffix=".wav") as source:
    source.write(buffer.getvalue())
    source.flush()
    with patch("app.services.transcription.load_model") as model:
        model.return_value.transcribe.return_value = {"text": "smoke check"}
        assert audio_transcript(source.name) == "smoke check"
print("Readiness, auth, shared HTTP/WebSocket Redis quota, and FFmpeg smoke checks passed")
