#!/usr/bin/env bash
# install-mu-plugin.sh — copy landing-config mu-plugin to Beget WP install.
# Usage: bash install-mu-plugin.sh <project-dir>
#
# Uploads mu-plugin/landing-config-loader.php to mu-plugins/ (WP auto-loads
# this top-level file), which requires mu-plugins/landing-config/landing-config.php.
# Falls back to tar+ssh if rsync isn't installed (e.g. plain Git Bash on Windows).

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
MU_ROOT="$SCRIPT_DIR/../mu-plugin"
MU_SRC="$MU_ROOT/landing-config"
LOADER_SRC="$MU_ROOT/landing-config-loader.php"

[ -d "$MU_SRC" ] || { echo "ERROR: $MU_SRC not found (mu-plugin source missing)" >&2; exit 1; }
[ -f "$LOADER_SRC" ] || { echo "ERROR: $LOADER_SRC not found (loader stub missing)" >&2; exit 1; }

REMOTE_MU_BASE="${BEGET_PATH}/wp-content/mu-plugins"
REMOTE_MU_DIR="${REMOTE_MU_BASE}/landing-config"
REMOTE_LOADER="${REMOTE_MU_BASE}/landing-config-loader.php"

SSH_OPTS="-i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

echo "▶ Prepare remote dirs"
ssh $SSH_OPTS "${BEGET_USER}@${BEGET_HOST}" \
    "mkdir -p ${REMOTE_MU_BASE} && rm -rf ${REMOTE_MU_DIR} && mkdir -p ${REMOTE_MU_DIR}"

if command -v rsync >/dev/null 2>&1; then
    echo "▶ rsync mu-plugin → ${BEGET_HOST}:${REMOTE_MU_DIR}"
    rsync -avz --delete \
        -e "ssh $SSH_OPTS" \
        "$MU_SRC/" \
        "${BEGET_USER}@${BEGET_HOST}:${REMOTE_MU_DIR}/" | tail -5
else
    echo "▶ tar+ssh upload (rsync unavailable)"
    tar -czf - -C "$MU_SRC" . | ssh $SSH_OPTS "${BEGET_USER}@${BEGET_HOST}" \
        "cd ${REMOTE_MU_DIR} && tar -xzf -"
fi

echo "▶ Upload loader stub"
scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    "$LOADER_SRC" "${BEGET_USER}@${BEGET_HOST}:${REMOTE_LOADER}"

echo "▶ Trigger DB schema install via wp option get"
# wp-cli on Beget shim is PHP 7.4 — call PHP 8.3 directly.
# Hit each site so init action runs maybe_install_or_migrate.
ssh $SSH_OPTS "${BEGET_USER}@${BEGET_HOST}" "
    WPCLI='/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=${BEGET_PATH}'
    for url in \$(\$WPCLI site list --field=url 2>/dev/null); do
        echo \"  - \$url\"
        \$WPCLI option get siteurl --url=\$url 2>&1 | tail -1
    done
"

echo "✅ landing-config mu-plugin installed at ${REMOTE_MU_DIR}"
echo "   Loader stub: ${REMOTE_LOADER}"
echo "   Visit any subsite's wp-admin and look for 'Лендинг' in the left menu."
