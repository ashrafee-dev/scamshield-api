import hashlib
import secrets

from fastapi import HTTPException, WebSocket, WebSocketException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
from redis.exceptions import RedisError

from app.config import API_KEYS
from app.services import rate_limit

bearer = HTTPBearer(auto_error=False)


def identify(token: str) -> str | None:
    if any(secrets.compare_digest(token.encode(), key.encode()) for key in API_KEYS):
        return hashlib.sha256(token.encode()).hexdigest()
    return None


def enforce_limit(identity: str):
    try:
        allowed = rate_limit.check_rate_limit(identity)
    except RedisError as exc:
        raise HTTPException(503, "Rate limiter unavailable") from exc
    if not allowed:
        raise HTTPException(
            429, "Rate limit exceeded", headers={"Retry-After": str(rate_limit.RATE_LIMIT_WINDOW)},
        )


def authorize(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    identity = identify(credentials.credentials) if credentials else None
    if identity is None:
        raise HTTPException(401, "Invalid or missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    enforce_limit(identity)
    return identity


def authorize_websocket(websocket: WebSocket) -> str:
    scheme, _, token = websocket.headers.get("authorization", "").partition(" ")
    identity = identify(token) if scheme.lower() == "bearer" else None
    if identity is None:
        raise WebSocketException(1008, "Invalid or missing bearer token")
    return identity
