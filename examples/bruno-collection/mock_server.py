"""Offline mock of the ScamShield API for the Bruno collection.

Standard library only. Binds to 127.0.0.1:8000 and makes no outbound requests.
Bodies of unauthorized requests are not read or processed; bodies of authorized requests
(including uploaded audio) are read and dropped without parsing or storing them.
Responses are fixed so the collection is deterministic.
"""
import json
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8000

# The only token this mock accepts. It is a fake value, not a real credential,
# and matches SCAMSHIELD_API_KEY in environments/local.bru.
MOCK_TOKEN = "mock-local-token-not-a-real-credential"

PROTECTED_PATHS = {"/text", "/audio"}

# Fixed response using the real field names, types and enum values.
ASSESSMENT = {
    "label": "Safe",
    "score": "Low",
    "certainty": 80,
    "reason": "Fixed mock response; no analysis was performed.",
}


def has_valid_token(header: str) -> bool:
    """Return True for `Bearer <MOCK_TOKEN>`; the scheme is case-insensitive."""
    scheme, _, token = header.partition(" ")
    return scheme.lower() == "bearer" and secrets.compare_digest(
        token.encode(), MOCK_TOKEN.encode()
    )


class MockHandler(BaseHTTPRequestHandler):
    """Serve fixed responses for /health, /ready, /text and /audio."""

    server_version = "ScamShieldMock"

    def _send_json(self, status, payload, headers=None):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)

    def _discard_body(self):
        """Read and drop the body of an authorized request without storing it."""
        try:
            remaining = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return
        while remaining > 0:
            chunk = self.rfile.read(min(remaining, 65536))
            if not chunk:
                break
            remaining -= len(chunk)

    def do_GET(self):  # pylint: disable=invalid-name
        """Handle the unauthenticated probes."""
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
        elif self.path == "/ready":
            self._send_json(200, {"status": "ready"})
        else:
            self._send_json(404, {"detail": "Not Found"})

    def do_POST(self):  # pylint: disable=invalid-name
        """Handle the protected analysis endpoints."""
        if self.path not in PROTECTED_PATHS:
            self._reject(404, {"detail": "Not Found"})
            return
        # Check the token from the headers alone, before touching the body.
        if not has_valid_token(self.headers.get("Authorization", "")):
            self._reject(
                401,
                {"detail": "Invalid or missing bearer token"},
                {"WWW-Authenticate": "Bearer"},
            )
            return
        self._discard_body()
        self._send_json(200, ASSESSMENT)

    def _reject(self, status, payload, headers=None):
        """Respond without reading the body, then close the connection.

        Closing tells the client not to reuse the connection, so the unread
        request data is dropped with it instead of being parsed as a new request.
        """
        self.close_connection = True
        self._send_json(status, payload, {"Connection": "close", **(headers or {})})


def main():
    """Run the mock until interrupted."""
    try:
        server = ThreadingHTTPServer((HOST, PORT), MockHandler)
    except OSError as exc:
        sys.exit(
            f"Could not bind {HOST}:{PORT} ({exc}). Another service may already be "
            "using this port; stop it and try again."
        )
    print(f"ScamShield mock listening on http://{HOST}:{PORT} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
