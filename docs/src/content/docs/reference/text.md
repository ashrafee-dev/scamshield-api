---
title: Text Endpoint
description: Analyze messages, email bodies, and selected browser text.
---

# POST /text

Requires `Authorization: Bearer <backend-token>` and `Content-Type: application/json`.

```json
{"body":"Congratulations! Pay a fee to claim $10,000."}
```

`body` must contain 1–10,000 characters after stripping whitespace. The HTTP body is
limited to 64 KiB, including JSON encoding. No sender field is required.

Example response:

```json
{"label":"Scam","score":"High","certainty":95,"reason":"Prize claim requires an upfront fee."}
```

`label` is `Scam`, `Scam Likely`, or `Safe`; `score` is `High`, `Medium`, or `Low`;
`certainty` is an integer from 0 to 100, not a calibrated probability.
See [errors](/reference/error/) for failure responses.
