#!/usr/bin/env bash
# scripts/validate-all.sh — thin wrapper around tools/api_validators/aggregate.py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env if present
[ -f .env ] && set -a && . ./.env && set +a

if [ "${1:-}" = "--service" ] && [ -n "${2:-}" ]; then
    python3 -c "
import sys
from tools.api_validators.aggregate import run_all
results = run_all(only=['$2'])
failed = 0
for r in results:
    print(r)
    if not r.is_valid:
        failed += 1
sys.exit(1 if failed else 0)
"
else
    python3 -m tools.api_validators.aggregate
fi
