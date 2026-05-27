#!/usr/bin/env bash
# scripts/landing-delete.sh — safely delete a landing project
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: landing-delete.sh <slug>"
    exit 1
fi

SLUG="$1"
LANDINGS_ROOT="${LANDINGS_ROOT:-$(python -c "import sys; sys.path.insert(0,'$REPO_ROOT'); from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)")}"
TARGET="$LANDINGS_ROOT/$SLUG"

if [ ! -d "$TARGET" ]; then
    echo "❌ Проект '$SLUG' не найден в $LANDINGS_ROOT"
    exit 1
fi

if [ ! -f "$TARGET/.landing-state.yaml" ]; then
    echo "❌ Папка существует, но это не лендинг-проект (нет .landing-state.yaml)"
    exit 1
fi

STAGE=$(grep '^current_stage:' "$TARGET/.landing-state.yaml" | awk '{print $2}' | tr -d '"' || echo "unknown")
[ -z "$STAGE" ] && STAGE="unknown"
FILE_COUNT=$(find "$TARGET" | wc -l | tr -d ' ')

echo ""
echo "Проект: $SLUG"
echo "Папка:  $TARGET"
echo "Файлов: $FILE_COUNT"
echo "Этап:   $STAGE"
echo ""
printf "Для подтверждения введи имя проекта: "
read -r CONFIRM

if [ "$CONFIRM" != "$SLUG" ]; then
    echo "❌ Имя не совпадает. Удаление отменено."
    exit 1
fi

rm -rf "$TARGET"
echo "✅ Проект $SLUG удалён."
