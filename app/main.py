from contextlib import asynccontextmanager
import asyncio
import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis.exceptions import RedisError
from app.api import analyze
from app.config import CORS_ORIGINS, validate_settings
from app.middleware import BodyLimitMiddleware
from app.services import rate_limit
from app.services.transcription import load_model


@asynccontextmanager
async def lifespan(_app):
    validate_settings()
    if os.getenv("PRELOAD_WHISPER", "false").lower() == "true":
        await asyncio.to_thread(load_model)
    yield

app = FastAPI(
    lifespan=lifespan,
    title="ScamShield API",
    description=(
        "Analyze text, email and audio content for scam risk. "
        "The API provides HTTP endpoints for email and audio analysis "
        "plus a WebSocket endpoint for streaming audio analysis."
    ),
)

app.add_middleware(BodyLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(analyze.router)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/ready", include_in_schema=False)
def readiness():
    try:
        rate_limit.r.ping()
    except RedisError as exc:
        raise HTTPException(503, "Redis unavailable") from exc
    return {"status": "ready"}
