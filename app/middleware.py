from fastapi import HTTPException
from starlette.formparsers import MultiPartException
from starlette.responses import JSONResponse

from app.config import MAX_FILE_SIZE
from app.services.auth import identify


class BodyLimitMiddleware:  # pylint: disable=too-few-public-methods
    """Count streamed request bytes, including requests without Content-Length."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        limit = MAX_FILE_SIZE + 65536 if scope["path"] == "/audio" else 65536
        headers = dict(scope["headers"])
        if scope["path"] in {"/text", "/email", "/audio"}:
            authorization = headers.get(b"authorization", b"").decode("latin-1")
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or identify(token) is None:
                response = JSONResponse(
                    {"detail": "Invalid or missing bearer token"}, 401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                return await response(scope, receive, send)
        try:
            length = int(headers.get(b"content-length", b"0"))
            if length < 0:
                raise ValueError
        except ValueError:
            response = JSONResponse({"detail": "Invalid Content-Length"}, 400)
            return await response(scope, receive, send)
        if length > limit:
            response = JSONResponse({"detail": "Request body too large"}, 413)
            return await response(scope, receive, send)
        total = 0

        async def bounded_receive():
            nonlocal total
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > limit:
                    if b"multipart/form-data" in headers.get(b"content-type", b"").lower():
                        # Starlette closes partially spooled files for this exception type.
                        raise MultiPartException("Request body too large")
                    raise HTTPException(413, "Request body too large")
            return message

        async def bounded_send(message):
            if total > limit and message["type"] == "http.response.start":
                # Starlette maps multipart parser failures to 400; size failures are 413.
                message = {**message, "status": 413}
            await send(message)

        return await self.app(scope, bounded_receive, bounded_send)
