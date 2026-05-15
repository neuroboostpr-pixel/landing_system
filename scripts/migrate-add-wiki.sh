#!/bin/bash
# scripts/migrate-add-wiki.sh
# Добавляет wiki/ и memory/ к существующему проекту-лендингу.
# Использование: bash scripts/migrate-add-wiki.sh ~/Lendings/<slug>

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Использование: $0 <путь к проекту>"
    echo "Пример: $0 ~/Lendings/dubai-avto-liza"
    exit 1
fi

PROJECT_DIR="$(cd "$1" && pwd)"
LANDING_SYSTEM_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$LANDING_SYSTEM_DIR/template"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: проект не найден: $PROJECT_DIR"
    exit 2
fi

echo "📚 Миграция wiki/ + memory/ в $PROJECT_DIR..."

mkdir -p "$PROJECT_DIR/wiki" "$PROJECT_DIR/memory"

# README placeholders (не перезаписываем если есть)
[ -f "$PROJECT_DIR/wiki/README.md" ] || cp "$TEMPLATE_DIR/wiki/README.md" "$PROJECT_DIR/wiki/README.md"
[ -f "$PROJECT_DIR/memory/README.md" ] || cp "$TEMPLATE_DIR/memory/README.md" "$PROJECT_DIR/memory/README.md"

# .gitignore
if [ -f "$PROJECT_DIR/.gitignore" ]; then
    if ! grep -q "memory/daily" "$PROJECT_DIR/.gitignore" 2>/dev/null; then
        echo "" >> "$PROJECT_DIR/.gitignore"
        cat "$TEMPLATE_DIR/.gitignore" >> "$PROJECT_DIR/.gitignore"
    fi
else
    cp "$TEMPLATE_DIR/.gitignore" "$PROJECT_DIR/.gitignore" 2>/dev/null || true
fi

# Первичная компиляция графа проекта
SLUG=$(basename "$PROJECT_DIR")

echo "▶️ Запускаю project-graph compile для '$SLUG'..."
cd "$LANDING_SYSTEM_DIR" && python3 -m scripts.wiki.compile --source-mode=project-graph --project="$SLUG"

echo ""
echo "✅ Готово. Открой $PROJECT_DIR/wiki/index.md"
