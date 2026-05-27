#!/usr/bin/env bash
# scripts/landing-rename.sh — rename a landing project and update internal references
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ $# -lt 2 ]; then
    echo "Usage: landing-rename.sh <old-slug> <new-slug>"
    exit 1
fi

OLD_SLUG="$1"
NEW_SLUG="$2"
LANDINGS_ROOT="${LANDINGS_ROOT:-$(python -c "import sys; sys.path.insert(0,'$REPO_ROOT'); from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)")}"
OLD_DIR="$LANDINGS_ROOT/$OLD_SLUG"
NEW_DIR="$LANDINGS_ROOT/$NEW_SLUG"

# Validate old slug
if [ ! -d "$OLD_DIR" ]; then
    echo "❌ Проект '$OLD_SLUG' не найден в $LANDINGS_ROOT"
    exit 1
fi
if [ ! -f "$OLD_DIR/.landing-state.yaml" ]; then
    echo "❌ Папка существует, но это не лендинг-проект (нет .landing-state.yaml)"
    exit 1
fi

# Validate new slug
if [ -d "$NEW_DIR" ]; then
    echo "❌ Проект '$NEW_SLUG' уже существует в $LANDINGS_ROOT"
    exit 1
fi
if ! echo "$NEW_SLUG" | grep -qE '^[a-z0-9-]+$'; then
    echo "❌ Slug должен быть kebab-case (только строчные буквы, цифры, дефис)"
    exit 1
fi

# Move folder
mv "$OLD_DIR" "$NEW_DIR"

# Update .landing-state.yaml
yq e ".project = \"$NEW_SLUG\"" -i "$NEW_DIR/.landing-state.yaml"

# Update README.md
if [ -f "$NEW_DIR/README.md" ]; then
    sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/README.md"
fi

# Update brief.md
if [ -f "$NEW_DIR/00_БРИФ/brief.md" ]; then
    sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/00_БРИФ/brief.md"
fi

# Update wiki/pipeline-map.md
if [ -f "$NEW_DIR/wiki/pipeline-map.md" ]; then
    sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/wiki/pipeline-map.md"
fi

UPDATED=0
[ -f "$NEW_DIR/README.md" ] && UPDATED=$((UPDATED + 1))
[ -f "$NEW_DIR/00_БРИФ/brief.md" ] && UPDATED=$((UPDATED + 1))
[ -f "$NEW_DIR/wiki/pipeline-map.md" ] && UPDATED=$((UPDATED + 1))

echo ""
echo "✅ Проект переименован: $OLD_SLUG → $NEW_SLUG"
echo "Папка: $NEW_DIR"
echo "Обновлено файлов: $UPDATED"
