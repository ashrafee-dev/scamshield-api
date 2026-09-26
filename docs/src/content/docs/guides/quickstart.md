---
title: Quick Start
description: Make an authenticated text or audio request.
---

Deploy your own instance using the [deployment guide](/guides/deployment/).
Set `SCAMSHIELD_API_KEY` in your client environment to one configured server token.
Replace the local URL with your HTTPS deployment URL for remote clients.

## Text analysis

```bash
curl http://localhost:8000/text \
  -H "Authorization: Bearer $SCAMSHIELD_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"body":"Congratulations! Pay a fee to claim $10,000."}'
```

## Audio analysis

```bash
curl http://localhost:8000/audio \
  -H "Authorization: Bearer $SCAMSHIELD_API_KEY" \
  -F 'file=@sample.mp3'
```

Text and transcripts are sent to DeepSeek after best-effort redaction; see
[privacy and client integration](/guides/privacy/) before connecting end users.
