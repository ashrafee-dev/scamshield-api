---
title: Audio Endpoint
description: Analyze uploaded audio.
---

# POST /audio

Uploads an audio file.

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
curl -X POST https://api.scamshield.click/audio \
-F "file=@audio.mp3"
```

Returns the same response schema as the Email endpoint.
