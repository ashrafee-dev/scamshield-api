---
title: Email Endpoint (Deprecated)
description: Compatibility alias for text analysis.
---

# POST /email

Use [`POST /text`](/reference/text/) for new integrations. `/email` accepts the same
`body`, optionally accepts an unused `sender` string, and returns the same assessment.
It requires the same bearer authentication and shares the token's rate quota.
