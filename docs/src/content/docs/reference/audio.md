---
title: Audio Endpoint
description: Analyze uploaded audio.
---

# POST /audio

Requires `Authorization: Bearer <backend-token>`. Upload a multipart field named `file`.
The default limits are 25 MiB and 120 seconds; the operator may configure both.
The service detects the file format from its bytes, decodes locally, and sends the
redacted transcript to DeepSeek. Only one inference per worker runs at a time;
busy workers return 503 with `Retry-After: 5`.

## Supported Formats

- MP3
- M4A
- MP4
- WAV
- WebM
- OGG
- FLAC

## Example

```bash
curl -X POST http://localhost:8000/audio \
-H "Authorization: Bearer $SCAMSHIELD_API_KEY" \
-F "file=@audio.mp3"
```

Returns the same response schema as the [Text endpoint](/reference/text/).
