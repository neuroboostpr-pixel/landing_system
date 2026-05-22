#!/usr/bin/env bash
# install_legal_pages.sh — генерирует policy.html и consent.html
# через render.py + создаёт WordPress Pages через wp-cli.
#
# Usage: bash install_legal_pages.sh <project-dir>
#
# Reads:
#   <project-dir>/04_БРЕНД/brand-kit.md (через parse_legal.py)
#   <project-dir>/.env (BEGET_USER/HOST/SSH_KEY/PATH)
#
# Creates on Beget:
#   wp post create --post_type=page --post_name=policy --post_title='...'
#   wp post create --post_type=page --post_name=consent --post_title='...'
#
# Idempotent: если Page с meta _lp_legal_page=policy|consent уже есть — wp post update.

set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-dir>" >&2
    exit 2
fi
PROJECT="$(cd "$PROJECT" && pwd)"

[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }
[ -f "$PROJECT/04_БРЕНД/brand-kit.md" ] || { echo "ERROR: brand-kit.md not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?missing in .env}"
: "${BEGET_HOST:?missing in .env}"
: "${BEGET_SSH_KEY:?missing in .env}"
: "${BEGET_PATH:?missing in .env}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PYTHON="${PYTHON:-python3}"

# Generate HTML through render.py
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PYTHONPATH="$SYSTEM_ROOT/skills/legal-pages-render/scripts:$SYSTEM_ROOT/skills/brand-kit-build/scripts" \
$PYTHON - <<EOF
import sys
sys.path.insert(0, "$SYSTEM_ROOT/skills/legal-pages-render/scripts")
sys.path.insert(0, "$SYSTEM_ROOT/skills/brand-kit-build/scripts")
from parse_legal import parse_legal_from_brand_kit
from render import render_policy, render_consent
import datetime

legal = parse_legal_from_brand_kit("$PROJECT/04_БРЕНД/brand-kit.md")
if legal is None:
    print("ERROR: legal section missing in brand-kit.md", file=sys.stderr)
    sys.exit(1)
if legal.get('_incomplete'):
    print("ERROR: legal section has TODO_LEGAL placeholders. Fill 04_БРЕНД/extracted/legal.yaml.", file=sys.stderr)
    sys.exit(1)

today = datetime.date.today().isoformat()
legal['effective_date'] = today
legal['last_updated'] = today

with open("$TMP_DIR/policy.html", "w", encoding="utf-8") as f:
    f.write(render_policy(legal))
with open("$TMP_DIR/consent.html", "w", encoding="utf-8") as f:
    f.write(render_consent(legal))

print("Generated policy.html and consent.html in $TMP_DIR")
EOF

# Upload to Beget
SSH="ssh -i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=ERROR ${BEGET_USER}@${BEGET_HOST}"
WP="/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=$BEGET_PATH"

scp -i "$BEGET_SSH_KEY" -o StrictHostKeyChecking=no \
    "$TMP_DIR/policy.html" "$TMP_DIR/consent.html" \
    "${BEGET_USER}@${BEGET_HOST}:/tmp/"

# Helper for idempotent create-or-update
upsert_page() {
    local slug="$1"
    local title="$2"
    local content_path="/tmp/${slug}.html"

    local existing_id=$($SSH "$WP post list --post_type=page --meta_key=_lp_legal_page --meta_value=$slug --format=ids" 2>/dev/null | head -1 | tr -d '[:space:]')

    if [ -n "$existing_id" ]; then
        $SSH "$WP post update $existing_id $content_path --post_title='$title'"
        $SSH "rm $content_path"
        echo "Updated existing /$slug page (id=$existing_id)"
    else
        local new_id=$($SSH "$WP post create $content_path --post_type=page --post_status=publish --post_name=$slug --post_title='$title' --porcelain")
        $SSH "$WP post meta update $new_id _lp_legal_page $slug"
        $SSH "rm $content_path"
        echo "Created /$slug page (id=$new_id)"
    fi
}

upsert_page policy "Политика обработки персональных данных"
upsert_page consent "Согласие на обработку персональных данных"

echo "✅ Legal pages installed"
