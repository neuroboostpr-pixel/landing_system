#!/usr/bin/env bash
# install-mu-plugin.sh — copy landing-config mu-plugin to Beget WP install.
# Usage: bash install-mu-plugin.sh <project-dir>

set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
    echo "Usage: install-mu-plugin.sh <project-dir>" >&2
    exit 2
fi

PROJECT="$(cd "$PROJECT" && pwd)"
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?missing in .env}"
: "${BEGET_HOST:?missing in .env}"
: "${BEGET_SSH_KEY:?missing in .env}"
: "${BEGET_PATH:?missing in .env}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MU_SRC="$SCRIPT_DIR/../mu-plugin/landing-config"

[ -d "$MU_SRC" ] || { echo "ERROR: $MU_SRC not found (mu-plugin source missing)" >&2; exit 1; }

REMOTE_MU_DIR="${BEGET_PATH}/wp-content/mu-plugins/landing-config"

SSH_OPTS="-i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

echo "▶ rsync mu-plugin → ${BEGET_HOST}:${REMOTE_MU_DIR}"
rsync -avz --delete \
    -e "ssh $SSH_OPTS" \
    "$MU_SRC/" \
    "${BEGET_USER}@${BEGET_HOST}:${REMOTE_MU_DIR}/" | tail -5

echo "▶ Trigger DB schema install via wp eval"
ssh $SSH_OPTS "${BEGET_USER}@${BEGET_HOST}" \
    "cd $BEGET_PATH && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --network option get siteurl 2>&1 | tail -1"

echo "✅ landing-config mu-plugin installed at ${REMOTE_MU_DIR}"
echo "   Visit any subsite's wp-admin and look for 'Лендинг' in the left menu."
