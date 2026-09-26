import asyncio
import os
import tempfile
import threading

import filetype
from fastapi import APIRouter, Depends, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from app.config import MAX_FILE_SIZE, CORS_ORIGINS
from app.models.response import riskAssessment
from app.models.request import TextRequest, information
from app.services.auth import authorize, authorize_websocket, enforce_limit
from app.services.risk import get_assessment, AssessmentUnavailable
from app.services.transcription import audio_transcript, InvalidAudio

router = APIRouter()
# Serialize model inference per worker; reject excess work instead of accumulating uploads.
audio_slot = threading.BoundedSemaphore(1)
Allowed = {"audio/mpeg", "audio/m4a", "audio/mp4", "audio/wav", "audio/x-wav",
           "audio/webm", "audio/ogg", "audio/flac"}
UNSUPPORTED_AUDIO_ERROR = (
    "Unsupported audio content type. Accepted formats: MP3, M4A, MP4, WAV, WebM, OGG, FLAC."
)


def assess(text: str) -> riskAssessment:
    try:
        return get_assessment(text)
    except AssessmentUnavailable as exc:
        raise HTTPException(502, "Assessment temporarily unavailable") from exc


@router.post(
    "/text", summary="Analyze text for scam risk", dependencies=[Depends(authorize)],
    responses={401: {"description": "Authentication required"},
               429: {"description": "Rate limit exceeded"}, 502: {"description": "Provider unavailable"}},
)
def text_check(item: TextRequest) -> riskAssessment:
    return assess(item.body)


@router.post(
    "/email", summary="Analyze email content for scam risk", deprecated=True,
    dependencies=[Depends(authorize)],
    responses={429: {"description": "Rate limit exceeded"}},
)
def email_check(item: information) -> riskAssessment:
    return assess(item.body)


def analyze_audio(data: bytes) -> riskAssessment:
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(413, {"error": f"File too large. Max size is {MAX_FILE_SIZE // (1024 * 1024)}MB."})
    kind = filetype.guess(data)
    if kind is None or kind.mime not in Allowed:
        raise HTTPException(415, {"error": UNSUPPORTED_AUDIO_ERROR})
    if not audio_slot.acquire(blocking=False):
        raise HTTPException(503, "Audio processor busy", headers={"Retry-After": "5"})
    try:
        with tempfile.TemporaryDirectory(prefix="scamshield-upload-") as directory:
            filename = os.path.join(directory, f"audio.{kind.extension}")
            with open(filename, "wb") as audio:
                audio.write(data)
            try:
                transcript = audio_transcript(filename)
            except InvalidAudio as exc:
                raise HTTPException(422, str(exc)) from exc
            return assess(transcript)
    finally:
        audio_slot.release()


@router.post(
    "/audio", summary="Analyze an audio file for scam risk", dependencies=[Depends(authorize)],
    responses={413: {"description": "Upload too large"}, 415: {"description": "Unsupported audio"},
               429: {"description": "Rate limit exceeded"}, 503: {"description": "Audio processor busy"}},
)
def audio_check(file: UploadFile) -> riskAssessment:
    return analyze_audio(file.file.read(MAX_FILE_SIZE + 1))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Analyze complete audio clips over an authenticated WebSocket connection.

    Each binary message is one independently decodable clip, not a partial stream.
    """
    identity = authorize_websocket(websocket)
    origin = websocket.headers.get("origin")
    if origin and origin not in CORS_ORIGINS:
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    await websocket.accept()
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=60)
                await asyncio.to_thread(enforce_limit, identity)
                result = await asyncio.to_thread(analyze_audio, data)
                await websocket.send_json(result.model_dump())
            except HTTPException as exc:
                error = exc.detail if isinstance(exc.detail, dict) else {"error": exc.detail}
                await websocket.send_json(error)
                if exc.status_code in (429, 503):
                    await websocket.close(code=1013)
                    return
            except asyncio.TimeoutError:
                await websocket.close(code=1000, reason="Idle timeout")
                return
            except KeyError:
                await websocket.close(code=1003, reason="Send binary audio messages")
                return
    except WebSocketDisconnect:
        return
