# Contributing to ScamShield

Your first contribution does not need to change application code. A clear example,
reproduced bug, or focused regression test is valuable. No AWS account, paid API key,
Redis server, or Whisper model download is needed for the normal test suite.

## Find a task

- Start with [ready good first issues](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22+label%3A%22status%3Aready%22).
- See [the contributor roadmap](contributor-roadmap/README.md) for areas and difficulty.
- Comment on an issue with your intended approach. Check for an existing PR before starting.
- `status:design-needed` means the approach or contract needs agreement, not that implementation is ready.
- `status:blocked` means a listed dependency must land first. Avoid basing a beginner PR on another feature branch.
- Ask for help in the issue if setup or the expected behavior is unclear. Partial findings are welcome.

## Run the existing tests

Install Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
git clone https://github.com/YOUR-USERNAME/scamshield-api.git
cd scamshield-api
uv sync --dev --frozen
uv run pytest
uv run pylint app tests
```

`tests/conftest.py` supplies test credentials, fake Redis, Whisper stubbing, and an
authenticated client. Endpoint tests must mock transcription and assessment where
they would otherwise run. Never use real private messages or recordings as fixtures.

Run one behavior while working:

```bash
uv run pytest tests/test_security.py::test_text_contract_and_legacy_email -q
```

Run the final Python checks from the repository root:

```bash
bash scripts/check.sh
```

The script runs tests before pylint and stops on failure. Audio fixture paths are
relative to the repository root. Do not install or run Redis just to fix unit tests.

## Documentation contributions

The website is a separate Astro/Starlight package:

```bash
cd docs
npm ci
npm run dev
# Before submitting:
npm run build
```

Use a supported Node release satisfying `docs/package-lock.json` engine requirements;
CI uses Node 22. Commit edited source, not `node_modules`, `.astro`, or `dist`.

## Small, independent pull requests

1. Fork the repository and create a branch from current upstream `main`.
2. Choose one issue with an agreed outcome and read its non-goals.
3. Prefer a focused new test/example file rather than unrelated changes to shared files.
4. Verify a regression test fails for the intended reason before fixing a confirmed bug.
5. Run the focused checks and the required package checks above.
6. Open a PR explaining behavior, verification, and any limitations; link its issue.

Use `Fixes #NUMBER` only when the PR satisfies the whole issue. For partial work,
use `Refs #NUMBER` and state what remains. Do not mix formatting, renaming, and new
behavior in one PR. Maintainers should coordinate changes to shared interfaces before
several contributors start editing them.

Do not build a PR on an unmerged PR without agreement. Newcomer tasks should work
against `main`; maintainers must refresh their file references after refactors.

## What needs design review

Authentication, privacy filtering changes, concurrency, quotas, public API contracts,
dependencies, and cloud architecture need an agreed approach and experienced review.
Tests documenting current behavior can usually be contributed independently.

Existing assessment enums and response envelopes are client contracts. `/text` is
the primary text endpoint; `/email` is a deprecated alias. Browser extensions must
not contain the backend API token. Treat external model output as untrusted.

## Running the live app

Follow [README.md](README.md) and the [deployment guide](docs/src/content/docs/guides/deployment.md).
This is separate from unit-test setup: real execution needs credentials and Redis,
and audio needs FFmpeg plus model weights. Live provider requests incur usage.

## Review and assistance

Include commands actually run, not a checked box claiming all tests pass. If you
cannot run a platform-specific check, say so. Never paste secrets or private input
into issues, logs, screenshots, or PRs.

The README's preference for human-authored contributions remains in effect. Authors
must understand and verify every submitted change, including any tool-assisted work.
An issue is an invitation to collaborate, not a requirement to finish without help.
