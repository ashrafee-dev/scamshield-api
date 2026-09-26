---
title: Rate Limits
description: Shared, atomic quotas per backend token.
---

Analysis uses a fixed-window quota per authenticated API token, shared across `/text`,
`/email`, `/audio`, and WebSocket audio messages. Defaults: 10 requests per 60 seconds.
Operators can configure `MAX_REQUEST_LIMIT` and `RATE_LIMIT_WINDOW`.

HTTP quota failures return 429 and a conservative `Retry-After` window in seconds:

```json
{"detail":"Rate limit exceeded"}
```

Redis 7+ transactions keep concurrent requests within the quota. Later requests do
not extend the window. Quotas reset on Redis restart; Redis outages fail closed with
503. Clients sharing a token share its quota, so bots/gateways must add per-user limits.
