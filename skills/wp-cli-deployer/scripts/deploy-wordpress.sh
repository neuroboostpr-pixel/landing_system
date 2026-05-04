#!/usr/bin/env bash
# skills/wp-cli-deployer/scripts/deploy-wordpress.sh
# Deploy wp-theme to Beget via rsync + wp-cli.
# Usage: deploy-wordpress.sh <project-dir>
set -euo pipefail

PROJECT="$(realpath "$1")"
PROJECT_SLUG="$(basename "$PROJECT")"
THEME_DIR="$PROJECT/08_КОД/wp-theme"
ACF_JSON="$PROJECT/08_КОД/acf-fields.json"

# Load .env from landing-system root (2 levels up from skills/wp-cli-deployer/scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../../.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

: "${BEGET_USER:?BEGET_USER not set in .env}"
: "${BEGET_HOST:?BEGET_HOST not set in .env}"
: "${BEGET_PATH:?BEGET_PATH not set in .env}"

REMOTE_THEME="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}"

echo "▶ Синхронизация темы → $BEGET_HOST:$REMOTE_THEME"
rsync -avz --delete \
  --exclude=".git" \
  --exclude="*.map" \
  "$THEME_DIR/" \
  "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"

echo "▶ Активация темы"
ssh "${BEGET_USER}@${BEGET_HOST}" \
  "wp theme activate lp-${PROJECT_SLUG} --path=${BEGET_PATH} --allow-root"

if [ -f "$ACF_JSON" ]; then
  echo "▶ Импорт ACF полей"
  ACF_CONTENT="$(cat "$ACF_JSON")"
  ssh "${BEGET_USER}@${BEGET_HOST}" \
    "echo '${ACF_CONTENT}' | wp acf import --json - --path=${BEGET_PATH} --allow-root" 2>/dev/null || true
fi

echo "▶ Очистка кэша"
ssh "${BEGET_USER}@${BEGET_HOST}" \
  "wp cache flush --path=${BEGET_PATH} --allow-root" 2>/dev/null || true

echo "✅ Деплой завершён → https://${BEGET_HOST}"
