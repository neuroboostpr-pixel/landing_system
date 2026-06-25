#!/usr/bin/env bash
# skills/wp-cli-deployer/scripts/deploy-wordpress.sh
# Deploy wp-theme to Beget via rsync + wp-cli, install Lazy Blocks,
# seed front page from page-content.html.
# Usage: deploy-wordpress.sh <project-dir> [--env staging|prod] [--confirm]
#   --env      Target environment (default: staging)
#   --confirm  Required when --env prod; safety gate for production deploys
set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../scripts/lib/python-cmd.sh"
PROJECT="$(realpath "$1")"
shift
PROJECT_SLUG="$(basename "$PROJECT")"
THEME_DIR="$PROJECT/08_КОД/wp-theme"
PAGE_HTML="$PROJECT/08_КОД/page-content.html"
SPEC="$PROJECT/08_КОД/block-spec.yaml"

# Parse optional flags
DEPLOY_ENV="staging"
CONFIRMED=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --env)      DEPLOY_ENV="$2"; shift 2 ;;
        --confirm)  CONFIRMED=1; shift ;;
        *)          echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

# Prod safety gate
if [[ "$DEPLOY_ENV" == "prod" && "$CONFIRMED" -eq 0 ]]; then
    echo "ERROR: deploying to prod requires --confirm flag." >&2
    echo "  Re-run: $0 <project-dir> --env prod --confirm" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load deploy-targets.yaml if present (overrides .env for host/user/path)
TARGETS_YAML="$PROJECT/09_ДЕПЛОЙ/deploy-targets.yaml"
if [ -f "$TARGETS_YAML" ]; then
    if command -v "$PYTHON_CMD" >/dev/null 2>&1; then
        _PY_CMD="$PYTHON_CMD"
    else
        _PY_CMD="python"
    fi
    while IFS= read -r line; do
        export "${line?}"
    done < <("$_PY_CMD" "$SCRIPT_DIR/get-deploy-target.py" "$TARGETS_YAML" "$DEPLOY_ENV")
fi

ENV_FILE="$SCRIPT_DIR/../../../.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"
# Per-project .env overrides system-level .env (e.g. BEGET_PATH per landing).
PROJECT_ENV="$PROJECT/.env"
[ -f "$PROJECT_ENV" ] && source "$PROJECT_ENV"

: "${BEGET_USER:?BEGET_USER not set in .env or deploy-targets.yaml}"
: "${BEGET_HOST:?BEGET_HOST not set in .env or deploy-targets.yaml}"
: "${BEGET_PATH:?BEGET_PATH not set in .env or deploy-targets.yaml}"

echo "▶ Deploying to: ${DEPLOY_ENV} (${BEGET_HOST})"

REMOTE_THEME="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}"
WP="wp --path=${BEGET_PATH} --allow-root"

ssh_run() { ssh "${BEGET_USER}@${BEGET_HOST}" "$@"; }

echo "▶ Backup DB → $PROJECT/09_ДЕПЛОЙ/backups/"
BACKUP_DIR="$PROJECT/09_ДЕПЛОЙ/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_TS=$(date +%Y%m%d-%H%M%S)
ssh_run "$WP db export /tmp/backup-${BACKUP_TS}.sql"
scp "${BEGET_USER}@${BEGET_HOST}:/tmp/backup-${BACKUP_TS}.sql" "${BACKUP_DIR}/"
ssh_run "rm -f /tmp/backup-${BACKUP_TS}.sql"
echo "  ✓ Saved to $BACKUP_DIR/backup-${BACKUP_TS}.sql"

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

echo "▶ Install plugins from design-stack.yaml + defaults"
STACK_YAML="$PROJECT/06_СТЕК/design-stack.yaml"
if command -v $PYTHON_CMD >/dev/null 2>&1; then
    PLUGIN_SLUGS=$("$PYTHON_CMD" "$SCRIPT_DIR/get-plugin-list.py" "$STACK_YAML" 2>/dev/null)
else
    PLUGIN_SLUGS=$("python" "$SCRIPT_DIR/get-plugin-list.py" "$STACK_YAML" 2>/dev/null)
fi
if [ -n "$PLUGIN_SLUGS" ]; then
    while IFS= read -r slug; do
        [ -z "$slug" ] && continue
        echo "  → $slug"
        ssh_run "$WP plugin is-installed ${slug} 2>/dev/null \
            || $WP plugin install ${slug} --activate 2>/dev/null \
            || true"
        ssh_run "$WP plugin is-active ${slug} 2>/dev/null \
            || $WP plugin activate ${slug} 2>/dev/null \
            || true"
    done <<< "$PLUGIN_SLUGS"
fi

echo "▶ Ensure lazy-blocks plugin"
ssh_run "$WP plugin is-installed lazy-blocks 2>/dev/null || $WP plugin install lazy-blocks --activate"
ssh_run "$WP plugin is-active lazy-blocks || $WP plugin activate lazy-blocks"

# ACF Free stays installed for potential page-level meta; no block-field import.
echo "▶ Ensure ACF Free (optional, for page-level meta)"
ssh_run "$WP plugin is-installed advanced-custom-fields 2>/dev/null || $WP plugin install advanced-custom-fields --activate" || true

# ── C4 (спека reference-driven §4.4): деплой забывал плагины проекта ──
echo "▶ Sync project plugins (08_КОД/plugins/ → wp-content/plugins/)"
PROJECT_PLUGINS_DIR="$PROJECT/08_КОД/plugins"
if [ -d "$PROJECT_PLUGINS_DIR" ]; then
    for plugdir in "$PROJECT_PLUGINS_DIR"/*/; do
        [ -d "$plugdir" ] || continue
        plugname="$(basename "$plugdir")"
        echo "  → $plugname"
        ssh_run "mkdir -p ${BEGET_PATH}/wp-content/plugins/${plugname}"
        if command -v rsync >/dev/null 2>&1; then
            rsync -avz --delete --exclude=".git" \
                "$plugdir" "${BEGET_USER}@${BEGET_HOST}:${BEGET_PATH}/wp-content/plugins/${plugname}/"
        else
            scp -r "$plugdir." "${BEGET_USER}@${BEGET_HOST}:${BEGET_PATH}/wp-content/plugins/${plugname}/"
        fi
        ssh_run "$WP plugin activate ${plugname} 2>/dev/null || true"
    done
else
    echo "  (нет $PROJECT_PLUGINS_DIR — пропуск)"
fi

# ── C4: деплой забывал .htaccess → REST/превью блоков ломались ──
# C4-fix (2026-06-22): для установки в ПОДПАПКУ (public_html/<slug>) RewriteBase
# обязан быть /<slug>/, иначе pretty-permalink REST (/wp-json/) уходит в корень
# домена → 404 → редактор Gutenberg падает «not a valid JSON response».
# Вычисляем subpath из BEGET_PATH (часть после .../public_html) и ВСЕГДА
# перезаписываем .htaccess (старый с RewriteBase / тоже чинится).
echo "▶ Ensure .htaccess + rewrite rules"
# subpath = всё после public_html/ ; для корня домена пусто → RewriteBase /
HT_SUBPATH="$(printf '%s' "$BEGET_PATH" | sed -E 's#.*/public_html##; s#^/+##; s#/+$##')"
if [ -n "$HT_SUBPATH" ]; then
    HT_BASE="/${HT_SUBPATH}/"
else
    HT_BASE="/"
fi
echo "  RewriteBase=${HT_BASE} (subdir-aware)"
ssh_run "cat > ${BEGET_PATH}/.htaccess <<HTEOF
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase ${HT_BASE}
RewriteRule ^index\\.php\$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . ${HT_BASE}index.php [L]
</IfModule>
# END WordPress
HTEOF"
ssh_run "$WP rewrite structure '/%postname%/' 2>/dev/null || true"
ssh_run "$WP rewrite flush --hard" || ssh_run "$WP rewrite flush" || true

# ── C4: favicon / site icon (см. docs/standards/logo-icon-favicon.md) ──
echo "▶ Site icon (favicon)"
FAVICON_SRC=""
for cand in "$PROJECT/04_БРЕНД/favicon/favicon-512.png" \
            "$PROJECT/04_БРЕНД/favicon/favicon.png" \
            "$THEME_DIR/assets/img/favicon-512.png"; do
    [ -f "$cand" ] && { FAVICON_SRC="$cand"; break; }
done
if [ -n "$FAVICON_SRC" ]; then
    scp "$FAVICON_SRC" "${BEGET_USER}@${BEGET_HOST}:/tmp/lp-favicon.png"
    FAV_ID="$(ssh_run "$WP media import /tmp/lp-favicon.png --porcelain" | tail -n1)"
    if [ -n "$FAV_ID" ]; then
        ssh_run "$WP option update site_icon ${FAV_ID}"
        echo "  site_icon → attachment $FAV_ID"
    fi
    ssh_run "rm -f /tmp/lp-favicon.png"
else
    echo "  (favicon не найден в 04_БРЕНД/favicon/ — пропуск; см. docs/standards/logo-icon-favicon.md)"
fi

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
    # Write photo map (fname|attachment_id, one per line) for fix-page-content-images.py
    PHOTO_MAP_TXT="$(mktemp)"
    for fname in "${!IMG_IDS[@]}"; do
        echo "${fname}|${IMG_IDS[$fname]}" >> "$PHOTO_MAP_TXT"
    done

    # fix-page-content-images.py делает 3 трансформации:
    # 1. __IMAGE_ATTACHMENT_ID__assets/photos/<fname>__ → real attachment ID
    # 2. "assets/photos/X.jpg" string paths → IDs (для card sub-blocks)
    # 3. URL-encode image attribute objects {"id":N,"url":""} в JSON string
    #    (Lazy Blocks image-control ожидает rawurlencode(json_encode(...)))
    if command -v $PYTHON_CMD >/dev/null 2>&1 && $PYTHON_CMD -c '' >/dev/null 2>&1; then
        PY=$PYTHON_CMD
    else
        PY=python
    fi
    "$PY" "$SCRIPT_DIR/fix-page-content-images.py" "$TMP_HTML" "$PHOTO_MAP_TXT" || {
        echo "ERROR: fix-page-content-images.py failed" >&2
        exit 1
    }
    rm -f "$PHOTO_MAP_TXT"

    # Convert MSYS-style /d/... to Windows D:/... when running Windows Python from Git Bash.
    SPEC_PY="$SPEC"
    if command -v cygpath >/dev/null 2>&1; then
        SPEC_PY="$(cygpath -w "$SPEC")"
    fi
    PAGE_SLUG="$($PY -c "import sys,yaml; d=yaml.safe_load(open(r'$SPEC_PY',encoding='utf-8')); print((d.get('page') or {}).get('slug') or 'home')")"
    PAGE_TITLE="$($PY -c "import sys,yaml; d=yaml.safe_load(open(r'$SPEC_PY',encoding='utf-8')); print((d.get('page') or {}).get('title') or 'Home')")"

    REMOTE_HTML="${BEGET_PATH}/wp-content/themes/lp-${PROJECT_SLUG}/.page-content.html"
    scp "$TMP_HTML" "${BEGET_USER}@${BEGET_HOST}:${REMOTE_HTML}"

    existing_page_id="$(ssh_run "$WP post list --post_type=page --name=${PAGE_SLUG} --field=ID" | head -n1 || true)"
    if [ -n "$existing_page_id" ]; then
        ssh_run "$WP post update ${existing_page_id} --post_content=\"\$(cat ${REMOTE_HTML})\" --post_status=publish"
        PAGE_ID="$existing_page_id"
    else
        PAGE_ID="$(ssh_run "$WP post create --post_type=page --post_status=publish --post_title='${PAGE_TITLE}' --post_name='${PAGE_SLUG}' --post_content=\"\$(cat ${REMOTE_HTML})\" --porcelain")"
    fi

    # Guard: KSES может экранировать вложенные блок-комментарии
    # (<!-- wp:lazyblock/* --> внутри section-card) в &lt;!-- … -->, из-за
    # чего блоки рендерятся сырым текстом. wp-cli в admin-контексте обычно
    # безопасен, но при программной записи это всплывает (см. asset-pipeline.md
    # «KSES экранирует вложенные блоки»). Проверяем и при необходимости
    # переписываем post_content напрямую в БД, минуя content-фильтры.
    escaped="$(ssh_run "$WP post get ${PAGE_ID} --field=content | grep -c '&lt;!-- wp:' || true" | head -n1)"
    if [ "${escaped:-0}" != "0" ]; then
        echo "⚠ KSES экранировал вложенные блоки — переписываю post_content напрямую"
        ssh_run "$WP eval 'global \$wpdb; \$wpdb->update(\$wpdb->posts, [\"post_content\"=>file_get_contents(\"${REMOTE_HTML}\")], [\"ID\"=>${PAGE_ID}]); clean_post_cache(${PAGE_ID});'"
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
