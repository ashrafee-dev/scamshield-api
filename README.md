# ScamShield API

A FastAPI-powered API for analyzing scam emails and scam audio using local transcription and AI-based risk assessment.

## Features
Risk Assessment for:
-  Email scam analysis
-  Audio file scam analysis (e.g. recorded call)
-  Real-time audio analysis over WebSockets (e.g. live call)

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
* Get your .env configured (look at example.env)
```bash
uv sync
uv run --env-file .env fastapi dev app/main.py
```

## Contributing

Contributions are welcome.

- Keep the code simple and readable.
- NOAI contributions are preferred.


- For First Time Contribution 
    - Look for issues labeled **`first-time-contribution`**. I'll keep them small and beginner-friendly so anyone can make their first contribution.
- Have fun!
