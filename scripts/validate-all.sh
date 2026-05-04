#!/usr/bin/env bash
# scripts/validate-all.sh — thin wrapper around tools/api_validators/aggregate.py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env if present
[ -f .env ] && set -a && . ./.env && set +a

if [ "${1:-}" = "--service" ] && [ -n "${2:-}" ]; then
    python3 -m tools.api_validators.aggregate --only "$2"
else
    python3 -m tools.api_validators.aggregate
fi
