from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze
from app.config import CORS_ORIGINS

app = FastAPI(
    title="ScamShield API",
    description=(
        "Analyze email and audio content for scam risk. "
        "The API provides HTTP endpoints for email and audio analysis "
        "plus a WebSocket endpoint for streaming audio analysis."
    ),
)


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
