#!/usr/bin/env bash
set -euo pipefail

echo "Running tests..."
uv run pytest

echo "Running lint..."
uv run pylint app tests
