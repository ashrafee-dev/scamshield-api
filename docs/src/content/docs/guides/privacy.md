---
title: Privacy and client integration
description: Understand data flow before connecting a bot or extension.
---

## Data flow

1. A trusted backend authenticates to ScamShield with its server-side bearer token.
2. Audio is decoded and transcribed locally using Whisper. Temporary files are
   removed on success and ordinary exceptions. The container tmpfs is ephemeral.
3. Text or the transcript is regex-filtered for email addresses, phone numbers,
   card-like numbers, US SSNs, and long digit sequences.
4. The filtered text is sent to **DeepSeek** for assessment.

The filter is best effort, not anonymization. Names, addresses, passwords, and other
personal information may remain. Do not promise that content stays entirely on your
server. Review the provider's current data policies for your account and jurisdiction.
The API does not persist content or assessment history, but your client, proxy,
hosting provider, and model provider may have their own retention policies.

## Clients

For a Discord bot, submit only content explicitly selected by the user, show that
analysis uses an external provider, and defer the interaction before waiting for audio.
Apply per-user quotas on the bot server. Never post a user's content publicly merely
because they requested analysis.

For a Chrome extension, request the minimum browser permissions and submit selected
content only after an explicit user action. Authenticate users to your own backend;
that backend enforces per-user quotas and holds the ScamShield API token. This repo
provides service-to-service authentication, not browser user registration or sessions.
Browser WebSocket clients cannot supply Authorization headers; use a backend bridge
or authenticated HTTP uploads through your gateway.

Do not log content, transcripts, authorization tokens, or model prompts. Do not send
tokens in query strings. Explain the data flow to users before submitting content.

## Interpreting results

The model's `certainty` is an uncalibrated estimate, not a measured probability.
False positives and false negatives are possible. Treat `Safe` as advisory and avoid
automatically deleting messages, banning users, or approving payments based solely
on the response. Untrusted text is separated from system instructions, but this does
not guarantee resistance to every prompt-injection attempt.
