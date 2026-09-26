import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


MAX_REQUEST_LIMIT = positive_int("MAX_REQUEST_LIMIT", 10)
RATE_LIMIT_WINDOW = positive_int("RATE_LIMIT_WINDOW", 60)
MAX_FILE_SIZE = positive_int("MAX_FILE_SIZE", 25 * 1024 * 1024)
MAX_AUDIO_SECONDS = positive_int("MAX_AUDIO_SECONDS", 120)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
API_KEYS = tuple(
    key.strip() for key in os.getenv("SCAMSHIELD_API_KEYS", "").split(",") if key.strip()
)
CORS_ORIGINS = [
    origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
]
if any("*" in origin for origin in CORS_ORIGINS):
    raise ValueError("CORS_ORIGINS must contain explicit origins; wildcards are not allowed.")


def validate_settings():
    if not API_KEYS or any(len(key) < 32 for key in API_KEYS):
        raise ValueError("SCAMSHIELD_API_KEYS must contain tokens of at least 32 characters")
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY is required")


@lru_cache(maxsize=1)
def get_ai_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
        timeout=20.0,
        max_retries=0,
    )
