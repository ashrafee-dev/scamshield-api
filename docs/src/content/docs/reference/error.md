---
title: Errors
description: Common API errors.
---

# Errors

## Rate Limited

```json
{
  "error":"Reached your limit, wait 60 seconds before requesting again"
}
```

## Unsupported Audio

```json
{
  "error": "Unsupported audio content type. Accepted formats: MP3, M4A, MP4, WAV, WebM, OGG, FLAC."
}
```

## File Too Large

```json
{
  "error": "File too large. Max size is 25MB."
}
```

## Invalid Request

```json
{
  "error":"Invalid request"
}
```
