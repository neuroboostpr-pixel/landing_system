#!/usr/bin/env bash
# scripts/validate-all.sh — thin wrapper around tools/api_validators/aggregate.py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Load .env if present
[ -f .env ] && set -a && . ./.env && set +a

PYTHON="${PYTHON:-$(command -v python3 2>/dev/null || command -v python)}"

echo "▶ Checking deploy-wordpress.sh installs lazy-blocks plugin"
if ! grep -qE '(\$WP|wp)[[:space:]]+plugin[[:space:]]+install[[:space:]]+lazy-blocks' skills/wp-cli-deployer/scripts/deploy-wordpress.sh; then
    echo "❌ deploy-wordpress.sh does not install lazy-blocks plugin — stage-08 won't work on prod"
    exit 1
fi

if [ "${1:-}" = "--service" ] && [ -n "${2:-}" ]; then
    "$PYTHON" -m tools.api_validators.aggregate --only "$2"
else
    "$PYTHON" -m tools.api_validators.aggregate
fi
