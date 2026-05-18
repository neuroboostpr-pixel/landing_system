#!/usr/bin/env bash
# landing-segment.sh — create a new audience segment subsite in multisite.
# Usage: bash landing-segment.sh <project-dir> <segment-slug>

set -euo pipefail

PROJECT="${1:-}"; SLUG="${2:-}"
if [ -z "$PROJECT" ] || [ -z "$SLUG" ]; then
    echo "Usage: landing-segment.sh <project-dir> <segment-slug>" >&2
    exit 2
fi
PROJECT="$(cd "$PROJECT" && pwd)"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

# Validate slug — only lowercase letters, digits, hyphens.
if ! [[ "$SLUG" =~ ^[a-z][a-z0-9-]*$ ]]; then
    echo "ERROR: slug must match ^[a-z][a-z0-9-]*$, got: $SLUG" >&2
    exit 2
fi

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?missing in .env}"; : "${BEGET_HOST:?}"; : "${BEGET_LOGIN:?}"
: "${BEGET_PASSWD:?}"; : "${BEGET_API:?}"; : "${BEGET_SSH_KEY:?}"
: "${BEGET_DOMAIN_ID:?}"; : "${BEGET_SITE_ID:?}"; : "${BEGET_PATH:?}"; : "${ROOT_DOMAIN:?}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/beget-api.sh"
source "$SCRIPT_DIR/lib/ssh-helpers.sh"
source "$SCRIPT_DIR/lib/state.sh"

# Phase 0: idempotency — fail-fast if slug already exists
if state_segment_exists "$STATE" "$SLUG"; then
    echo "ERROR: segment '$SLUG' already exists in $STATE" >&2
    exit 2
fi

# Phase 1: auto-migrate to multisite if needed
if ! state_is_multisite "$STATE"; then
    echo "▶ Project is single-site — running migrate-to-multisite.sh first"
    bash "$SCRIPT_DIR/migrate-to-multisite.sh" "$PROJECT"
fi

HOST="${SLUG}.${ROOT_DOMAIN}"
echo "▶ Creating segment '$SLUG' at $HOST"

# Phase 2: Beget subdomain (idempotent — skip if exists)
if ! beget_subdomain_exists "$HOST"; then
    NEW_SUB_ID=$(beget_subdomain_add "$SLUG" "$BEGET_DOMAIN_ID")
    echo "  Beget subdomain created (id=$NEW_SUB_ID)"
else
    NEW_SUB_ID=$(beget_subdomain_id "$HOST")
    echo "  Beget subdomain already exists (id=$NEW_SUB_ID)"
fi
beget_site_link "$NEW_SUB_ID" "$BEGET_SITE_ID"
beget_set_php "$HOST" "8.3"

echo "  (Phase 3: WP subsite — implemented in next Task)"
