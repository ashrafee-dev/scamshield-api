---
title: WebSocket
description: Real-time audio analysis.
---

# WebSocket

```
wss://api.scamshield.click/ws
```

## Supported Formats

- MP3
- M4A
- MP4
- WAV
- WebM
- OGG
- FLAC

## Flow

1. Connect.
2. Send an audio file as binary.
3. ScamShield transcribes the audio.
4. ScamShield analyzes the transcript.
5. Receive a JSON response.

Example response:

```json
{
  "label":"Safe",
  "score":0.08,
  "certainty":"High",
  "reason":"No suspicious language detected."
}
```
