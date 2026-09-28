---
title: Make your first contribution
description: Find a small task, run local tests, and submit an independent pull request.
---

You do not need an AWS account or a paid API key to contribute. The normal Python
tests use fake credentials, Redis, and model responses. Documentation and client
examples are useful contributions too.

## Pick an issue that is ready

- [Ready good first issues](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22+label%3A%22status%3Aready%22)
- [All ready tasks](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3A%22contributor-roadmap%22+label%3A%22status%3Aready%22)
- [Design discussions](https://github.com/ashrafee-dev/scamshield-api/issues?q=is%3Aissue+is%3Aopen+label%3A%22contributor-roadmap%22+label%3A%22status%3Adesign-needed%22)
- [Roadmap and issue index](https://github.com/ashrafee-dev/scamshield-api/tree/main/contributor-roadmap)

Read the acceptance criteria, intended file scope, and non-goals. Comment on the
issue before starting so others know what you are exploring. If a task says
`design-needed`, discuss it first rather than assuming its implementation is approved.

## Start with a local test

After installing Python 3.13+ and uv, fork and clone the repository, then run from
its root:

```bash
uv sync --dev --frozen
uv run pytest tests/test_security.py::test_text_contract_and_legacy_email -q
```

For Python changes, run the full local checks before submitting:

```bash
bash scripts/check.sh
```

For the documentation website:

```bash
cd docs
npm ci
npm run dev
# Check the final site:
npm run build
```

## Keep your first PR focused

Start from current upstream `main`, not another contributor's feature branch.
Address one agreed outcome. A dedicated test, example, or guide file usually causes
fewer merge conflicts than a broad refactor of shared code.

List the commands you actually ran and anything you could not verify. Ask for help
if the issue's paths or assumptions no longer match the code. You do not need to
solve an architectural problem just to add a useful regression test.

See [CONTRIBUTING.md](https://github.com/ashrafee-dev/scamshield-api/blob/main/CONTRIBUTING.md)
for the complete workflow. Never submit real credentials, private scam messages,
or personal recordings in an issue or fixture.
