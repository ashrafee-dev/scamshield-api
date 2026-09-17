import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
MAX_REQUEST_LIMIT = 10
RATE_LIMIT_WINDOW = 60

# Max allowed upload size for audio endpoints (e.g. voice notes).
# Configurable via env var so it isn't a hardcoded magic number scattered across files.
MAX_FILE_SIZE = int(os.environ.get(
    "MAX_FILE_SIZE", 25 * 1024 * 1024))  # 25 MB default


# Allowed CORS origins
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if any("*" in origin for origin in CORS_ORIGINS):
    raise ValueError("CORS_ORIGINS must contain explicit origins; wildcards are not allowed.")

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
