#!/usr/bin/env bash
# migrate-to-multisite.sh — convert single-site WP on Beget to subdomain multisite.
# Usage: bash migrate-to-multisite.sh <project-dir>
# Idempotent: re-running on already-multisite project is a no-op.
#
# Required env (from <project>/.env):
#   BEGET_USER, BEGET_HOST, BEGET_LOGIN, BEGET_PASSWD, BEGET_API,
#   BEGET_SSH_KEY, BEGET_DOMAIN_ID, BEGET_PATH, ROOT_DOMAIN

set -euo pipefail

PROJECT="${1:?Usage: migrate-to-multisite.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

# Load .env
set -a
# shellcheck disable=SC1090
source "$PROJECT/.env"
set +a

: "${BEGET_USER:?missing in .env}"
: "${BEGET_HOST:?missing in .env}"
: "${BEGET_LOGIN:?missing in .env}"
: "${BEGET_PASSWD:?missing in .env}"
: "${BEGET_API:?missing in .env}"
: "${BEGET_SSH_KEY:?missing in .env}"
: "${BEGET_DOMAIN_ID:?missing in .env}"
: "${BEGET_PATH:?missing in .env}"
: "${ROOT_DOMAIN:?missing in .env}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/beget-api.sh"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/ssh-helpers.sh"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/lib/state.sh"

# Phase 0: idempotency check
if state_is_multisite "$STATE"; then
    echo "OK: project is already multisite — nothing to do"
    exit 0
fi

# Phase 1: wildcard DNS
echo "▶ Phase 1: ensure *.${ROOT_DOMAIN} wildcard subdomain exists"
WILDCARD_FQDN="*.${ROOT_DOMAIN}"
if ! beget_subdomain_exists "$WILDCARD_FQDN"; then
    WC_ID=$(beget_subdomain_add "*" "$BEGET_DOMAIN_ID")
    echo "  created wildcard subdomain id=$WC_ID"
else
    echo "  wildcard already exists"
fi

# Phase 2: ensure linkDomain + PHP 8.3 for root and wildcard
echo "▶ Phase 2: link domain + PHP 8.3"
SITE_ID="${BEGET_SITE_ID:-}"
if [ -z "$SITE_ID" ]; then
    echo "  ERROR: BEGET_SITE_ID not in .env. Run beget_api site/getList to find it." >&2
    echo "  Add BEGET_SITE_ID=<id> to <project>/.env and re-run." >&2
    exit 2
fi
beget_site_link "$BEGET_DOMAIN_ID" "$SITE_ID" || echo "  (already linked)"
WC_ID=$(beget_subdomain_id "$WILDCARD_FQDN") || true
beget_site_link "$WC_ID" "$SITE_ID" || echo "  (already linked)"
beget_set_php "$ROOT_DOMAIN" "8.3"
beget_set_php "$WILDCARD_FQDN" "8.3"

# Phase 3: WP multisite convert
echo "▶ Phase 3: WordPress multisite-convert"
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN config set WP_ALLOW_MULTISITE true --raw" || true
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN core multisite-convert --subdomains" || \
    { echo "ERROR: multisite-convert failed" >&2; exit 3; }

# Phase 4: rewrite .htaccess
echo "▶ Phase 4: write multisite .htaccess"
ssh_beget "cat > $BEGET_PATH/.htaccess <<'HTACCESS'
RewriteEngine On
RewriteBase /
RewriteRule ^index\\.php\$ - [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?wp-admin\$ \$1wp-admin/ [R=301,L]
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(wp-(content|admin|includes).*) \$2 [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(.*\\.php)\$ \$2 [L]
RewriteRule . index.php [L]
HTACCESS"

# Phase 5: network-activate plugins
echo "▶ Phase 5: network-activate lazy-blocks + seo-by-rank-math"
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN plugin install lazy-blocks --activate-network" || true
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN plugin install seo-by-rank-math --activate-network" || true

# Phase 6: state — flip multisite flag
echo "▶ Phase 6: update state"
state_set_multisite_true "$STATE"

echo "✅ Migration complete. Project is now multisite."
