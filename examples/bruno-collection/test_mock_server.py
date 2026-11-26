"""Tests for the offline mock server's authentication handling.

Standard library only. Each test talks to a real MockHandler over loopback on an
ephemeral port, so it cannot clash with a service on port 8000 and makes no
outbound requests.
"""
import http.client
import json
import socket
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest import mock

import mock_server

BODY = json.dumps({"body": "hello"})
JSON_HEADERS = {"Content-Type": "application/json"}


class MockAuthTest(unittest.TestCase):
    """Unauthorized requests get an immediate 401 without reading the body."""

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), mock_server.MockHandler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def post(self, headers):
        """POST a small JSON body to /text and return (status, challenge, body)."""
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        try:
            conn.request("POST", "/text", BODY, {**JSON_HEADERS, **headers})
            response = conn.getresponse()
            return response.status, response.getheader("WWW-Authenticate"), response.read()
        finally:
            conn.close()

    def test_unauthorized_returns_401_and_never_reads_body(self):
        cases = {
            "missing token": {},
            "invalid token": {"Authorization": "Bearer wrong"},
        }
        for name, headers in cases.items():
            with self.subTest(name), mock.patch.object(
                mock_server.MockHandler, "_discard_body"
            ) as discard:
                status, challenge, data = self.post(headers)
                self.assertEqual(status, 401)
                self.assertEqual(challenge, "Bearer")
                self.assertEqual(
                    json.loads(data), {"detail": "Invalid or missing bearer token"}
                )
                discard.assert_not_called()

    def test_unsent_body_does_not_delay_401(self):
        # The headers promise a large body that is never sent. If the server tried
        # to read it, it would block and the recv below would time out.
        request = (
            b"POST /text HTTP/1.1\r\nHost: localhost\r\n"
            b"Content-Length: 1000000\r\n\r\n"
        )
        with socket.create_connection(("127.0.0.1", self.port), timeout=3) as conn:
            conn.sendall(request)
            self.assertTrue(conn.recv(4096).startswith(b"HTTP/1.0 401"))

    def test_valid_token_returns_200_and_calls_discard_body(self):
        token = "Bearer " + mock_server.MOCK_TOKEN
        with mock.patch.object(
            mock_server.MockHandler, "_discard_body", autospec=True
        ) as discard:
            status, _, data = self.post({"Authorization": token})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data), mock_server.ASSESSMENT)
        discard.assert_called_once()


if __name__ == "__main__":
    unittest.main()
