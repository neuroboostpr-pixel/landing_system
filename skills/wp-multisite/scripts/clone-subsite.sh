#!/usr/bin/env bash
# clone-subsite.sh — copy content from one multisite subsite to a new one.
# Usage: bash clone-subsite.sh <project-dir> <source-slug> <dest-slug>
# Byte-for-byte: copies all pages (title + content). siteurl/home are
# auto-managed by wp site create.

set -euo pipefail

PROJECT="${1:-}"; SOURCE_SLUG="${2:-}"; DEST_SLUG="${3:-}"
if [ -z "$PROJECT" ] || [ -z "$SOURCE_SLUG" ] || [ -z "$DEST_SLUG" ]; then
    echo "Usage: clone-subsite.sh <project-dir> <source-slug> <dest-slug>" >&2
    exit 2
fi
PROJECT="$(cd "$PROJECT" && pwd)"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?}"; : "${BEGET_HOST:?}"; : "${BEGET_LOGIN:?}"
: "${BEGET_PASSWD:?}"; : "${BEGET_API:?}"; : "${BEGET_SSH_KEY:?}"
: "${BEGET_DOMAIN_ID:?}"; : "${BEGET_SITE_ID:?}"; : "${BEGET_PATH:?}"; : "${ROOT_DOMAIN:?}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/beget-api.sh"
source "$SCRIPT_DIR/lib/ssh-helpers.sh"
source "$SCRIPT_DIR/lib/state.sh"

# Validation
if ! state_segment_exists "$STATE" "$SOURCE_SLUG"; then
    echo "ERROR: source segment '$SOURCE_SLUG' does not exist in state" >&2
    exit 2
fi
if state_segment_exists "$STATE" "$DEST_SLUG"; then
    echo "ERROR: destination segment '$DEST_SLUG' already exists" >&2
    exit 2
fi

SOURCE_URL="http://${SOURCE_SLUG}.${ROOT_DOMAIN}"
DEST_URL="http://${DEST_SLUG}.${ROOT_DOMAIN}"

# Step 1: create dest segment (subdomain + WP site + skeleton)
echo "▶ Step 1: create destination segment '$DEST_SLUG'"
bash "$SCRIPT_DIR/landing-segment.sh" "$PROJECT" "$DEST_SLUG"

# Step 2: copy all pages from source to dest
echo "▶ Step 2: copy pages $SOURCE_URL → $DEST_URL"
PAGE_IDS=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post list --post_type=page --post_status=publish --field=ID")
for src_id in $PAGE_IDS; do
    [ -z "$src_id" ] && continue
    TITLE=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $src_id --field=post_title" | tr -d '\r')
    CONTENT=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $src_id --field=post_content")
    NAME=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $src_id --field=post_name" | tr -d '\r')

    # Write content to temp remote file to avoid shell-escape issues
    REMOTE_TMP="/tmp/clone-$DEST_SLUG-$src_id.html"
    ssh_beget "cat > $REMOTE_TMP <<'CLONE_EOF'
$CONTENT
CLONE_EOF"
    # Pipe tempfile to wp-cli via stdin (avoids shell-escape issues with quotes in content)
    NEW_ID=$(ssh_beget "cd $BEGET_PATH && cat $REMOTE_TMP | $REMOTE_WP_BIN --url=$DEST_URL post create --post_type=page --post_status=publish --post_title=\"$TITLE\" --post_name=\"$NAME\" --post_content=- --porcelain" | tail -1 | tr -d '\r')
    ssh_beget "rm -f $REMOTE_TMP" 2>/dev/null || true
    echo "  page $src_id → $NEW_ID"
done

# Step 3: copy show_on_front + page_on_front (homepage continuity)
ON_FRONT=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "option get show_on_front" | tr -d '\r')
PAGE_FRONT_ID=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "option get page_on_front" | tr -d '\r')
if [ "$ON_FRONT" = "page" ] && [ -n "$PAGE_FRONT_ID" ]; then
    # The new page IDs differ; for now copy front-page by post_name match.
    FRONT_NAME=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $PAGE_FRONT_ID --field=post_name" | tr -d '\r')
    NEW_FRONT_ID=$(wp_remote_url "$BEGET_PATH" "$DEST_URL" "post list --post_type=page --name=$FRONT_NAME --field=ID" | head -1 | tr -d '\r')
    if [ -n "$NEW_FRONT_ID" ]; then
        wp_remote_url "$BEGET_PATH" "$DEST_URL" "option update show_on_front page" > /dev/null
        wp_remote_url "$BEGET_PATH" "$DEST_URL" "option update page_on_front $NEW_FRONT_ID" > /dev/null
        echo "  page_on_front → $NEW_FRONT_ID"
    fi
fi

echo "✅ Clone complete → $DEST_URL"
