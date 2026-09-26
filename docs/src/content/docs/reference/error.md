---
title: Errors
description: HTTP statuses and WebSocket failure handling.
---

| HTTP status | Meaning |
| --- | --- |
| 401 | Missing or invalid bearer token |
| 413 | File or total request body exceeds the limit |
| 415 | Unsupported audio format |
| 422 | Invalid text, invalid audio, excessive duration, or no detected speech |
| 429 | Token quota exceeded; honor `Retry-After` |
| 502 | Assessment provider unavailable or returned invalid output |
| 503 | Redis unavailable, server overloaded, or audio processor busy |

HTTP errors use FastAPI's `detail` envelope. File size and format errors preserve
the legacy `{"detail":{"error":"..."}}` shape; ordinary service errors use
`{"detail":"..."}` and validation errors use an array in `detail`.

WebSocket application errors use `{"error":"..."}`. See the
[WebSocket reference](/reference/websocket/) for handshake and close-code behavior.
Never interpret a failed analysis as a `Safe` verdict.
