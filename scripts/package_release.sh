#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PACKAGE_NAME="RLdC-Trading-bot-${TIMESTAMP}.zip"

mkdir -p "${DIST_DIR}"

echo "Running audit..."
python3 "${ROOT_DIR}/scripts/audit_repo.py"

echo "Creating package ${PACKAGE_NAME}..."
cd "${ROOT_DIR}"
zip -r "${DIST_DIR}/${PACKAGE_NAME}" . \
  -x ".git/*" \
  -x "dist/*" \
  -x "node_modules/*" \
  -x "__pycache__/*" \
  -x ".venv/*" \
  -x "venv/*"

echo "Package created at ${DIST_DIR}/${PACKAGE_NAME}"
