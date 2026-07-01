#!/usr/bin/env bash
set -euo pipefail
echo "=== PipeOne Pipeline Runner ==="
cd "$(dirname "$0")/.."
[ -f .env ] && export $(grep -v '^#' .env | xargs)
python ingestion/pipeline.py
