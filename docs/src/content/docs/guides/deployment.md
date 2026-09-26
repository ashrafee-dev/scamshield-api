---
title: Deployment
description: Deploy the authenticated text and audio API with Redis and Docker Compose.
---

## Configure

Use a host with Docker Compose v2. The supplied configuration allocates up to 6 GiB
to the API and 256 MiB to Redis; leave additional RAM for the OS. CPU-only Whisper
`turbo` needs substantial memory and may be slower than the clip duration. Benchmark
your workload; choose a smaller `WHISPER_MODEL` if appropriate and re-evaluate accuracy.

From the repository root:

```bash
cp example.env .env
openssl rand -hex 32
```

Set `SCAMSHIELD_API_KEYS` to the generated token and `DEEPSEEK_API_KEY` to your provider
key in `.env`. The app refuses startup with missing credentials or backend tokens
shorter than 32 characters. Use one random token per trusted backend; comma-separated
tokens allow rotation. Protect `.env` with `chmod 600 .env`.

```bash
docker compose up --build -d
docker compose logs -f api
```

The container runs as a non-root user with a read-only root filesystem, bounded tmpfs,
and a persistent Whisper cache. Compose preloads Whisper before serving requests;
the first startup downloads model weights and can take several minutes. It requires
outbound access to the model download host and DeepSeek. Never put credentials in images.

Redis is private to the Compose network. It uses Redis 7+ atomic transactions for a
fixed-window quota per API token, shared across HTTP and WebSocket requests. Its data
is ephemeral: restarting Redis resets quotas. Redis failure or memory exhaustion
fails analysis closed with 503. It never stores submitted text or audio.

## HTTPS and networking

Only `127.0.0.1:8000` is exposed on the host. Put an HTTPS reverse proxy in front of
it; do not bind the raw API or Redis port to the public internet. For example, a
host-installed Caddy with DNS pointing to this host can use:

```text
api.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Allow ports 80/443 for Caddy certificate provisioning. If using a different proxy,
enable WebSocket upgrades and allow enough response time for bounded audio inference.
Enforce connection and request-body timeouts at the proxy to limit slow clients.
The shipped server ignores forwarded headers: quotas use the authenticated token,
not an IP address supplied by clients. Access logs are disabled on the API server;
avoid logging request bodies or Authorization headers at the proxy as well.

Keep `CORS_ORIGINS` empty for server-to-server clients. If needed, list explicit
browser origins separated by commas; wildcards are rejected. CORS is not authentication.
WebSockets also reject an Origin header unless it is listed. Tokens belong in
Authorization headers, never URLs. Do not put the shared token in a browser extension.

## Limits and capacity

- Text: 1–10,000 characters after stripping whitespace; HTTP bodies capped at 64 KiB.
- Audio: `MAX_FILE_SIZE` bytes (default 25 MiB) and `MAX_AUDIO_SECONDS` (default 120).
  Multipart bodies allow 64 KiB overhead. Validation counts streamed bodies too.
- FFmpeg decoding times out after 30 seconds; inference accepts one clip at a time
  per worker. Other audio requests receive 503 rather than queueing unbounded work.
- The server uses one worker, caps concurrent connections at 32, and bounds WebSocket
  frames and queues. WebSocket compression is disabled; idle connections close after 60 seconds.
- `MAX_REQUEST_LIMIT` defaults to 10 requests per `RATE_LIMIT_WINDOW` of 60 seconds,
  per token. Gateway/bot per-user limits and provider spending limits are still needed.
- Provider calls have a 20-second timeout with SDK retries disabled. At most two
  attempts are made for malformed output. Network errors return 502 without retrying.

Do not increase worker count casually: each worker loads another model and admits
another simultaneous inference. Scale deliberately after measuring memory and latency.
Adjust container memory/tmpfs limits when increasing upload or duration limits.

## Rollout checks

```bash
docker compose ps
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
```

`/ready` checks Redis and is only served after startup completes. It does not verify
provider balance, upstream availability, or transcription accuracy. With a client
token exported as `SCAMSHIELD_API_KEY`, perform live checks (these incur provider usage):

```bash
curl -f http://127.0.0.1:8000/text \
  -H "Authorization: Bearer $SCAMSHIELD_API_KEY" \
  -H 'Content-Type: application/json' -d '{"body":"Please send the meeting agenda"}'
curl -f http://127.0.0.1:8000/audio \
  -H "Authorization: Bearer $SCAMSHIELD_API_KEY" -F 'file=@tests/test_audio.m4a'
```

Also verify unauthenticated requests receive 401 and repeated requests receive 429.
CI tests contracts with mocked services and builds/smoke-tests the container; it
does not call DeepSeek or download Whisper weights. Run the live checks on your host
before a public rollout. Monitor 429/502/503 rates, memory, latency, and provider spend.

Rotate keys by temporarily adding a new token, recreating the API, moving clients,
then removing the old token and recreating again. Each token has a separate quota.
For updates, keep the previous image tag, rebuild and verify readiness; roll back
to that image if smoke checks fail. There are no database migrations.
