---
title: Change dependencies
description: Update the Python (uv) and docs (npm) lockfiles separately, without unrelated upgrades.
---

This repository has two separate dependency sets. Each has its own lockfile.

| Part | Manifest | Lockfile | Tool |
| --- | --- | --- | --- |
| API and tests | `pyproject.toml` | `uv.lock` | uv |
| Documentation site | `docs/package.json` | `docs/package-lock.json` | npm |

A change to one does not touch the other. Do not update both in one pull request
unless the change really needs it. Adding a new dependency needs agreement in the
issue first. `CONTRIBUTING.md` lists dependencies under "What needs design review".

## Frozen installs

Day to day, install exactly what the lockfile says and do not let the tool change it.

```bash
# Python, from the repository root
uv sync --dev --frozen

# Docs, from the docs/ directory
npm ci
```

`uv sync --frozen` installs from `uv.lock` without updating it. `npm ci` installs
from `package-lock.json` and deletes any existing `node_modules` first. If
`package.json` and `package-lock.json` disagree, `npm ci` stops with an error
instead of fixing the lockfile. CI uses `uv sync --frozen --dev` and `npm ci`.

Use the commands below only when you mean to change a dependency.

## Python dependencies (uv)

Run these from the repository root. Python 3.13 or newer is required.

Check that `uv.lock` matches `pyproject.toml` without changing it:

```bash
uv lock --check
```

If the lockfile is out of date, this prints an error and tells you to run `uv lock`.

### Upgrade one package

```bash
uv lock --upgrade-package redis
```

This lets only `redis` move to a newer version that `pyproject.toml` allows. Other
packages stay at their locked versions, unless the new `redis` needs a different
version of one of its own dependencies. Do not use `uv lock --upgrade`. It
allows every package to move.

If the new version is outside the range in `pyproject.toml`, edit the range there
first, then run the same command.

### Add or remove a package

```bash
uv add --no-sync fastapi-example        # runtime dependency
uv add --no-sync --dev pytest-example   # dev dependency group
uv remove --no-sync fastapi-example
```

The package names above are placeholders. `--no-sync` updates `pyproject.toml` and
`uv.lock` without touching your virtual environment. Run
`uv sync --dev --frozen` afterwards to install the result.

### Keep the Linux CPU PyTorch source

`pyproject.toml` sends `torch` to the CPU index on Linux only:

```toml
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = [{ index = "pytorch-cpu", marker = "sys_platform == 'linux'" }]
```

Do not remove or reword these two blocks when you change other dependencies.
After any `uv.lock` change, confirm the lockfile still has both `torch` entries:

```bash
git diff pyproject.toml
grep -n 'whl/cpu' uv.lock
```

`git diff pyproject.toml` should show nothing in these blocks. The `grep` should
still print lines with `https://download.pytorch.org/whl/cpu`, including the
`torch` entry with `sys_platform == 'linux'`. If you only upgraded one unrelated
package, the `torch` entries should not change in the diff at all.

### Review the lockfile diff

```bash
git diff --stat -- pyproject.toml uv.lock
git diff -- uv.lock
```

Check that:

- Only the package you meant to change has a new `version`, `sdist` and `wheels`
  entry. Its own dependencies may change too.
- No other package changed version for no reason.
- The `torch` source stays as described above.

Then run the normal Python checks:

```bash
uv sync --dev --frozen
bash scripts/check.sh
```

## Documentation dependencies (npm)

Run these from the `docs/` directory. CI uses Node 22. The lockfile requires a
Node version that satisfies its `engines` fields, so use a supported release.

### Upgrade one package

```bash
npm update sharp --package-lock-only
```

This updates `package-lock.json` for `sharp` within the range in `package.json`.
It does not install anything. To move past that range, install a specific version:

```bash
npm install sharp@0.35 --package-lock-only
```

`npm install <package>@<version>` also edits the range in `package.json` (for
`sharp@0.35` it wrote `^0.35.5`). Do not run
a bare `npm update`, because it can move every package.

### Add or remove a package

```bash
npm install --save-dev example-package --package-lock-only
npm uninstall example-package --package-lock-only
```

`example-package` is a placeholder. These edit `package.json` and
`package-lock.json` only. Run `npm ci` afterwards to install the result.

### Review the lockfile diff

```bash
git diff --stat -- docs/package.json docs/package-lock.json
git diff -- docs/package-lock.json
```

Check that only the package you meant to change, and the packages it pulls in,
have new versions. Also look for large unrelated changes. In a test on Windows,
`npm install --package-lock-only` with no dependency change (npm 11.7.0, and also
npm 10.9.9) removed every `"libc"` entry for the optional `@img/sharp-*` packages
from the lockfile. That is unrelated churn. If you see it, put those entries back
(for example, discard the file with git and redo the change, or edit the lines back
by hand) rather than committing the removal. Ask in the issue if you are unsure.

Then run the same checks CI runs:

```bash
npm ci
npm run build
```

## Before you open a pull request

- Commit only the manifest and lockfile for the part you changed.
- Run `git diff --check`.
- Run the checks for that part (`bash scripts/check.sh` or `npm run build`).
- In the pull request, say which package you changed and why, and paste the commands
  you ran.
