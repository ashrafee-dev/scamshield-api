import os
import asyncio
import filetype
from fastapi import APIRouter, HTTPException, WebSocketException, UploadFile, WebSocket, WebSocketDisconnect, Request
from app.services import rate_limit
from app.models.response import riskAssessment
from app.models.request import information
from app.services.risk import get_assessment
from app.services.transcription import audio_transcript
from app.config import MAX_FILE_SIZE
import uuid
router = APIRouter()

Allowed = {
    "audio/mpeg",
    "audio/m4a",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/webm",
    "audio/ogg",
    "audio/flac",
}
SUPPORTED_AUDIO_FORMATS = ("MP3", "M4A", "MP4", "WAV", "WebM", "OGG", "FLAC")

UNSUPPORTED_AUDIO_ERROR = (
    "Unsupported audio content type. "
    f"Accepted formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}."
)

@router.post(
    "/email",
    summary="Analyze email content for scam risk",
    description=(
        "Analyze the submitted email body and return a scam risk assessment. "
        "Requests are rate-limited per client."
    ),
    responses={
        429: {"description": "Rate limit exceeded."},
    },
)
def email_check(item: information, request: Request)-> riskAssessment | dict | None:
    assert request.client is not None
    if not rate_limit.check_rate_limit(request.client.host):
        raise HTTPException (status_code= 429, detail= {"error":"Reached your limit, wait 60 seconds before requesting again"})
    return get_assessment(item.body)

@router.post(
    "/audio",
    summary="Analyze an audio file for scam risk",
    description=(
        "Upload a supported audio file for transcription and scam risk analysis. "
        "The endpoint enforces the configured maximum file size and validates "
        "the detected audio format."
    ),
    responses={
        413: {"description": "Uploaded audio exceeds the configured size limit."},
        415: {"description": "Uploaded content is not a supported audio format."},
        429: {"description": "Rate limit exceeded."},
    },
)
def audio_check(file:UploadFile, request: Request)-> riskAssessment | dict | None:


    assert request.client is not None
    if not rate_limit.check_rate_limit(request.client.host):
        raise HTTPException (status_code= 429, detail= {"error":"Reached your limit, wait 60 seconds before requesting again"})
    byte =  file.file.read()
    if len(byte) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail={"error": f"File too large. Max size is {MAX_FILE_SIZE // (1024 * 1024)}MB."})
    kind = filetype.guess(byte)

    if kind is None or kind.mime not in Allowed:
        raise HTTPException (status_code= 415, detail= {"error": UNSUPPORTED_AUDIO_ERROR})
    tmp_dir = "/dev/shm/" if os.path.exists("/dev/shm") else ""
    filename = f"{tmp_dir}audio{uuid.uuid4()}.{kind.extension}"
    with open(filename, "wb") as f:
        f.write(byte)
    transcript = audio_transcript(filename)
    os.remove(filename)
    return get_assessment(transcript)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket)-> riskAssessment | str | None:
    """Analyze streaming audio over a WebSocket connection.

    The client sends audio bytes. Supported audio is transcribed and analyzed,
    while oversized or unsupported payloads receive an error response.
    """
    await websocket.accept()

    try:
        while True:

            byte = await websocket.receive_bytes()

            assert websocket.client is not None
            if not rate_limit.check_rate_limit(websocket.client.host):
                raise WebSocketException(code = 1008, reason="Reached your limit, wait 60 seconds before requesting again")
            if len(byte) > MAX_FILE_SIZE:
                await websocket.send_json({"error": f"File too large. Max size is {MAX_FILE_SIZE // (1024 * 1024)}MB."})
                continue
            kind = filetype.guess(byte) 

            if kind is None or kind.mime not in Allowed:
                await websocket.send_json({"error": UNSUPPORTED_AUDIO_ERROR})
                continue
            tmp_dir = "/dev/shm/" if os.path.exists("/dev/shm") else ""
            filename = f"{tmp_dir}audio{uuid.uuid4()}.{kind.extension}"
            with open(filename, "wb") as f:
                f.write(byte)
            transcript = await asyncio.to_thread(audio_transcript,filename)
            os.remove(filename)
            assessment =  await asyncio.to_thread(get_assessment,transcript)
            if assessment is None: 
                await websocket.send_json({"error": "Failed to analyze the audio. Try again"})
            else:
                await websocket.send_json(assessment.model_dump())
    except WebSocketDisconnect:
        print("Client disconnected")
