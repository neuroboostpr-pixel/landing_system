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
