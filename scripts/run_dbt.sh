#!/usr/bin/env bash
set -euo pipefail
echo "=== Running dbt ==="
cd "$(dirname "$0")/../dbt"
[ -f ../.env ] && export $(grep -v '^#' ../.env | xargs)
dbt deps && dbt run && dbt test
