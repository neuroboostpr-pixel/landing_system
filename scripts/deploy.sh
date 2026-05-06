#!/usr/bin/env bash
# scripts/deploy.sh — Landing deploy orchestrator
# Usage: deploy.sh <project-dir>
set -euo pipefail

PROJECT="$(realpath "${1:?Usage: deploy.sh <project-dir>}")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKIP_PREFLIGHT="${2:-}"

echo "=== Landing Deploy: $(basename "$PROJECT") ==="
echo ""

# Preflight
if [ "$SKIP_PREFLIGHT" != "--skip-preflight" ]; then
  echo "▶ Preflight check"
  bash "$SCRIPT_DIR/preflight.sh" || exit 1
else
  echo "⚠ Preflight skipped"
fi

# Validate build exists
[ -f "$PROJECT/08_КОД/wp-theme/functions.php" ] \
  || { echo "❌ wp-theme не найден — запусти /landing-build"; exit 1; }

# Deploy
bash "$SCRIPT_DIR/../skills/wp-cli-deployer/scripts/deploy-wordpress.sh" "$PROJECT"

echo ""
echo "✅ Готово! Проверь сайт и запусти /landing-qa"
