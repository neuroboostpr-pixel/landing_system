#!/usr/bin/env bash
# skills/wp-cli-deployer/scripts/deploy-wordpress.sh
# Deploy wp-theme to Beget via rsync + wp-cli, install Lazy Blocks,
# seed front page from page-content.html.
# Usage: deploy-wordpress.sh <project-dir>
set -euo pipefail

PROJECT="$(realpath "$1")"
PROJECT_SLUG="$(basename "$PROJECT")"
THEME_DIR="$PROJECT/08_КОД/wp-theme"
PAGE_HTML="$PROJECT/08_КОД/page-content.html"
SPEC="$PROJECT/08_КОД/block-spec.yaml"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../../.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

: "${BEGET_USER:?BEGET_USER not set in .env}"
: "${BEGET_HOST:?BEGET_HOST not set in .env}"
: "${BEGET_PATH:?BEGET_PATH not set in .env}"

REMOTE_THEME="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}"
WP="wp --path=${BEGET_PATH} --allow-root"

ssh_run() { ssh "${BEGET_USER}@${BEGET_HOST}" "$@"; }

echo "▶ Sync theme → $BEGET_HOST:$REMOTE_THEME"
ssh_run "mkdir -p ${REMOTE_THEME}"
if command -v rsync >/dev/null 2>&1; then
    rsync -avz --delete --exclude=".git" --exclude="*.map" \
        "$THEME_DIR/" "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"
else
    scp -r "$THEME_DIR/." "${BEGET_USER}@${BEGET_HOST}:${REMOTE_THEME}/"
fi

echo "▶ Activate theme"
ssh_run "$WP theme activate lp-${PROJECT_SLUG}"

echo "▶ Ensure lazy-blocks plugin"
ssh_run "$WP plugin is-installed lazy-blocks 2>/dev/null || $WP plugin install lazy-blocks --activate"
ssh_run "$WP plugin is-active lazy-blocks || $WP plugin activate lazy-blocks"

# ACF Free stays installed for potential page-level meta; no block-field import.
echo "▶ Ensure ACF Free (optional, for page-level meta)"
ssh_run "$WP plugin is-installed advanced-custom-fields 2>/dev/null || $WP plugin install advanced-custom-fields --activate" || true

echo "▶ Import theme images into Media Library"
declare -A IMG_IDS=()
if [ -d "$THEME_DIR/assets/img" ]; then
    for img in "$THEME_DIR/assets/img"/*; do
        [ -f "$img" ] || continue
        fname="$(basename "$img")"
        remote_img="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}/assets/img/${fname}"
        # Idempotent: reuse existing attachment when present.
        slug_name="$(basename "$fname" | sed 's/\.[^.]*$//')"
        existing_id="$(ssh_run "$WP post list --post_type=attachment --name=${slug_name} --field=ID" | head -n1 || true)"
        if [ -n "$existing_id" ]; then
            att_id="$existing_id"
        else
            att_id="$(ssh_run "$WP media import ${remote_img} --porcelain")"
        fi
        IMG_IDS["$fname"]="$att_id"
        echo "    $fname → attachment $att_id"
    done
fi

if [ -f "$PAGE_HTML" ]; then
    echo "▶ Seed front page from page-content.html"
    TMP_HTML="$(mktemp)"
    cp "$PAGE_HTML" "$TMP_HTML"
    # Replace __IMAGE_ATTACHMENT_ID__<fname>__ with the bare integer ID.
    # generate-page-content.py emits this placeholder UNQUOTED in JSON so the
    # final result is `"id": 42`, a proper JSON integer.
    for fname in "${!IMG_IDS[@]}"; do
        id="${IMG_IDS[$fname]}"
        sed -i.bak "s|__IMAGE_ATTACHMENT_ID__${fname}__|${id}|g" "$TMP_HTML"
    done

    # Resolve a working Python (Windows ships `python`, Linux/mac ship `python3`)
    if command -v python3 >/dev/null 2>&1 && python3 -c '' >/dev/null 2>&1; then
        PY=python3
    else
        PY=python
    fi
    PAGE_SLUG="$($PY -c "import sys,yaml; d=yaml.safe_load(open(r'$SPEC',encoding='utf-8')); print((d.get('page') or {}).get('slug') or 'home')")"
    PAGE_TITLE="$($PY -c "import sys,yaml; d=yaml.safe_load(open(r'$SPEC',encoding='utf-8')); print((d.get('page') or {}).get('title') or 'Home')")"

    REMOTE_HTML="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}/.page-content.html"
    scp "$TMP_HTML" "${BEGET_USER}@${BEGET_HOST}:${REMOTE_HTML}"

    existing_page_id="$(ssh_run "$WP post list --post_type=page --name=${PAGE_SLUG} --field=ID" | head -n1 || true)"
    if [ -n "$existing_page_id" ]; then
        ssh_run "$WP post update ${existing_page_id} --post_content=\"\$(cat ${REMOTE_HTML})\" --post_status=publish"
        PAGE_ID="$existing_page_id"
    else
        PAGE_ID="$(ssh_run "$WP post create --post_type=page --post_status=publish --post_title='${PAGE_TITLE}' --post_name='${PAGE_SLUG}' --post_content=\"\$(cat ${REMOTE_HTML})\" --porcelain")"
    fi

    ssh_run "$WP option update show_on_front page"
    ssh_run "$WP option update page_on_front ${PAGE_ID}"
    ssh_run "rm -f ${REMOTE_HTML}"
    rm -f "$TMP_HTML" "$TMP_HTML.bak"
    echo "    page_on_front → ${PAGE_ID} (${PAGE_SLUG})"
fi

echo "▶ Cache flush"
ssh_run "$WP cache flush" 2>/dev/null || true

echo "✅ Deploy complete → https://${BEGET_HOST}"
