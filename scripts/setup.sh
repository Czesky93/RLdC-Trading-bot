#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install with: curl -Ls https://astral.sh/uv/install.sh | sh"
  exit 1
fi

uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
