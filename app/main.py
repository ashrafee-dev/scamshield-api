from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyze
from app.config import CORS_ORIGINS

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(analyze.router)
