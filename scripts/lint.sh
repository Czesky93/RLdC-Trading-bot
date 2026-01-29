#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
ruff check src tests
black --check src tests
mypy src
