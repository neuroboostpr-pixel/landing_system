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
# Create remote dir
ssh "${BEGET_USER}@${BEGET_HOST}" "mkdir -p ${REMOTE_THEME}"
# Use scp if rsync not available
if command -v rsync >/dev/null 2>&1; then
  rsync -avz --delete \
    --exclude=".git" \
    --exclude="*.map" \
    "$THEME_DIR/" \
    "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"
else
  echo "  (rsync not found, using scp)"
  scp -r "$THEME_DIR/." "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"
fi

echo "▶ Активация темы"
ssh "${BEGET_USER}@${BEGET_HOST}" \
  "wp theme activate lp-${PROJECT_SLUG} --path=${BEGET_PATH} --allow-root"

if [ -f "$ACF_JSON" ]; then
    echo "▶ Проверяю что ACF активен на сервере"
    if ! ssh "${BEGET_USER}@${BEGET_HOST}" \
        "wp plugin is-active advanced-custom-fields --path=${BEGET_PATH} --allow-root" 2>/dev/null; then
        echo "❌ Плагин ACF не активен на сервере."
        echo "   Сначала установите и активируйте его:"
        echo "   ssh ${BEGET_USER}@${BEGET_HOST} \"wp plugin install advanced-custom-fields --activate --path=${BEGET_PATH} --allow-root\""
        exit 1
    fi
    echo "▶ Импорт ACF полей"
    ACF_CONTENT="$(cat "$ACF_JSON")"
    if ! ssh "${BEGET_USER}@${BEGET_HOST}" \
        "echo '${ACF_CONTENT}' | wp acf import --json - --path=${BEGET_PATH} --allow-root"; then
        echo "❌ wp acf import не прошёл. Проверьте формат $ACF_JSON и доступ ACF на сервере."
        exit 1
    fi
fi

echo "▶ Очистка кэша"
ssh "${BEGET_USER}@${BEGET_HOST}" \
  "wp cache flush --path=${BEGET_PATH} --allow-root" 2>/dev/null || true

echo "✅ Деплой завершён → https://${BEGET_HOST}"
