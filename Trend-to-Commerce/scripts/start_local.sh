#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

export TREND_TO_COMMERCE_DATA_DIR="${TREND_TO_COMMERCE_DATA_DIR:-$ROOT_DIR/Data}"
export TREND_TO_COMMERCE_DB_PATH="${TREND_TO_COMMERCE_DB_PATH:-$ROOT_DIR/backend/trend_to_commerce.db}"
export TREND_TO_COMMERCE_LOAD_RTF_ENV="${TREND_TO_COMMERCE_LOAD_RTF_ENV:-1}"
export GENERATION_PREFER_REMOTE="${GENERATION_PREFER_REMOTE:-1}"

echo "Starting Trend-to-Commerce at http://127.0.0.1:8000"
uvicorn backend.app.main:app --host 127.0.0.1 --port "${TREND_TO_COMMERCE_PORT:-8000}"
