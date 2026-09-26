# ScamShield API

A FastAPI API for assessing scam risk in text and audio. Whisper transcribes audio locally;
DeepSeek analyzes the text. Results are advisory, not a guarantee of safety.

## Features
Authenticated endpoints:
- `POST /text` — messages, emails, or selected browser text (`{"body":"..."}`).
- `POST /audio` — a multipart upload named `file`.
- `WS /ws` — one complete, decodable audio clip per binary message.
- `POST /email` — deprecated compatibility alias; optional `sender` is ignored.

All analysis requires `Authorization: Bearer <token>` from `SCAMSHIELD_API_KEYS`.
`GET /health` is liveness; `GET /ready` checks Redis. Neither probes DeepSeek.

## Project Structure

```text
app/
├── api/          # HTTP & WebSocket routes
├── models/       # Request and response models
├── services/     # AI, transcription, audio processing
├── config.py
└── main.py

tests/
```

## Getting Started
Requires Python 3.13+, uv, Redis 7+, and the **FFmpeg executable** for audio.
Copy `example.env` to `.env`, set `DEEPSEEK_API_KEY`, and generate a backend token with
`openssl rand -hex 32` for `SCAMSHIELD_API_KEYS`. Keep `.env` out of version control.

```bash
uv sync --dev --frozen
uv run --env-file .env fastapi dev app/main.py
```

```bash
curl http://localhost:8000/text \
  -H "Authorization: Bearer $SCAMSHIELD_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"body":"Pay this fee now to claim your prize"}'
```

Export `SCAMSHIELD_API_KEY` in your client shell to one of the server's configured tokens.
Run `bash scripts/check.sh` for tests followed by lint. Tests use fake credentials,
Redis, and Whisper; they make no paid provider calls.

## Deployment and clients

See [the deployment guide](docs/src/content/docs/guides/deployment.md) for Docker Compose,
TLS proxying, resource limits, credential rotation, and rollout checks. The Linux image
uses CPU-only PyTorch; benchmark Whisper on the target host before accepting public traffic.

- **Discord:** keep the API token on the bot server; defer interactions before audio analysis.
  The bot must enforce per-user quotas; the API quota is shared by all users of that token.
- **Chrome extension:** use your own user-authenticated backend as a gateway. Do not embed
  a shared ScamShield or DeepSeek key in extension code. Browser WebSockets cannot set an
  Authorization header; proxy those connections through the backend, or use HTTP uploads.

Text and transcripts are sent to DeepSeek after best-effort regex redaction. Redaction
does **not** remove every kind of personal data. Ask users before submitting content;
see the [privacy and integration notes](docs/src/content/docs/guides/privacy.md).

## Contributing

Contributions are welcome.

- Keep the code simple and readable.
- NOAI contributions are preferred.


- For First Time Contribution 
    - Look for issues labeled **`first-time-contribution`**. I'll keep them small and beginner-friendly so anyone can make their first contribution.
- Have fun!
