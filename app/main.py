from fastapi import FastAPI
from app.api import analyze

app = FastAPI()
app.include_router(analyze.router)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
