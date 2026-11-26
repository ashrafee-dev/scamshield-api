# ScamShield Bruno collection

A [Bruno](https://www.usebruno.com/) collection for the ScamShield API, plus a small
offline mock server so you can try it without credentials, Redis, FFmpeg, model weights
or any paid provider call.

## Contents

| Path | Purpose |
| --- | --- |
| `bruno.json` | Collection definition |
| `environments/local.bru` | `baseUrl` and `SCAMSHIELD_API_KEY` for the `local` environment |
| `Health/health.bru` | `GET /health` (no auth) |
| `Health/ready.bru` | `GET /ready` (no auth) |
| `Analyze/text.bru` | `POST /text` (JSON body, bearer auth) |
| `Analyze/audio.bru` | `POST /audio` (multipart field `file`, bearer auth) |
| `Analyze/text-invalid-token.bru` | `POST /text` with a wrong token; expects 401 |
| `mock_server.py` | Standard-library mock of the four endpoints |
| `test_mock_server.py` | Standard-library `unittest` tests for the mock's authentication handling |

## Local base URL and placeholder token

The `local` environment sets:

- `baseUrl` = `http://127.0.0.1:8000`
- `SCAMSHIELD_API_KEY` = `mock-local-token-not-a-real-credential`

The token is a fake placeholder that only the mock server accepts. It is not a real
credential. The invalid-token request uses a different fake value
(`invalid-fake-token-for-401-demo`).

To point the collection at a real server, do **not** commit a real token. Override
`SCAMSHIELD_API_KEY` locally, for example as a Bruno secret variable or in a file that
is not tracked by git. A real server enforces a quota (10 requests per 60 seconds per
token by default), so repeated runs can return 429, and live `/text` and `/audio`
calls incur provider usage.

## Run the mock server

Needs Python 3.13+ and nothing else. From the repository root:

```bash
python3 examples/bruno-collection/mock_server.py
```

It listens only on `127.0.0.1:8000` and stops with Ctrl+C.

> **Port warning:** the mock uses the same port as the real API's default
> (`8000`). If another service, including a real ScamShield server, is already using
> it, the mock exits with an error. Stop that service first so requests never reach
> a real server by mistake.

### Mock behavior

- `GET /health` returns `200 {"status":"ok"}`; `GET /ready` returns `200 {"status":"ready"}`.
  Neither needs a token.
- `POST /text` and `POST /audio` require `Authorization: Bearer mock-local-token-not-a-real-credential`.
  Any other token, or none, gets `401 {"detail":"Invalid or missing bearer token"}` with
  `WWW-Authenticate: Bearer`. The token is checked from the headers before the body is
  read; unauthorized requests get the 401 immediately and the connection is closed.
- With the right token both return the same fixed assessment
  (`label`, `score`, `certainty`, `reason`) using the real field names and enum values.
- Bodies of unauthorized requests are not read or processed. Bodies of authorized
  requests and uploads are read and discarded without parsing. Nothing is stored and nothing leaves your machine.
- Because unauthorized bodies are not consumed, a client sending a large unauthorized
  upload may see a connection reset instead of receiving the complete 401 response. The
  small invalid-token request in this collection is not affected.
- It does not simulate 413, 415, 422, 429, 502 or 503, or the Redis-unavailable `/ready` 503.

## Import the collection in the Bruno app

1. Open Bruno and choose **Open Collection**.
2. Select the `examples/bruno-collection` folder.
3. Choose the **local** environment in the environment selector.
4. Start the mock server, then send the requests.

## Run the collection offline from the command line

With the mock server running in one terminal, in a second terminal:

```bash
cd examples/bruno-collection
bru run -r --env local
```

Expected: all requests pass. `/health` and `/ready` return 200, `/text` and `/audio`
return 200 with a valid assessment, and the invalid-token request returns 401.

The audio request uploads the repository's existing `tests/test_audio.m4a` through the
relative path `../../tests/test_audio.m4a`, so run the collection from inside the
repository. Do not point the audio request at a real server with private recordings.

## Test the mock server

The mock's authentication behavior has its own standard-library tests. They start a
throwaway server on an ephemeral port, so the mock does not need to be running and
port 8000 is not used. From the repository root:

```bash
python3 -m unittest discover -s examples/bruno-collection -p "test_*.py"
```

They check that a missing or invalid token with a JSON body gets `401` with
`WWW-Authenticate: Bearer`, that unauthorized bodies are not read (including a request
that declares a large body and never sends it), and that a valid token gets `200` with
the fixed assessment.

## Assertions

The requests check status codes, field types and the documented enums and ranges
(`label` is `Scam`, `Scam Likely` or `Safe`; `score` is `High`, `Medium` or `Low`;
`certainty` is an integer from 0 to 100). They do not assert specific labels, because
real model output varies.
