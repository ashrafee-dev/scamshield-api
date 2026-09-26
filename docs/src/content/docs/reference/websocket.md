---
title: WebSocket
description: Analyze complete audio clips over an authenticated connection.
---

# WS /ws

Connect to `wss://your-api.example/ws` with `Authorization: Bearer <backend-token>`
in the handshake. Tokens in URLs are not supported. Browser WebSockets cannot set
this header; use a trusted backend bridge or HTTP uploads via your gateway.
If the handshake includes an Origin, it must be in `CORS_ORIGINS`.

Send one complete, independently decodable audio file per binary message. This is
clip-by-clip analysis, not continuous partial-frame streaming. Formats and limits
match [`/audio`](/reference/audio/). Wait for a response before sending the next clip.

```json
{"label":"Safe","score":"Low","certainty":80,"reason":"No suspicious language detected."}
```

Errors use `{"error":"..."}`. Text frames close with code 1003, idle connections
close after 60 seconds, and rate-limited/unavailable connections close with 1013.
The supplied Uvicorn configuration closes over-limit frames with 1009 before inference.
Rejected handshakes may appear as HTTP 403 rather than a WebSocket close event.
