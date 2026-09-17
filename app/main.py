from fastapi import FastAPI
from app.api import analyze

app = FastAPI(
    title="ScamShield API",
    description=(
        "Analyze email and audio content for scam risk. "
        "The API provides HTTP endpoints for email and audio analysis "
        "plus a WebSocket endpoint for streaming audio analysis."
    ),
)
app.include_router(analyze.router)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
