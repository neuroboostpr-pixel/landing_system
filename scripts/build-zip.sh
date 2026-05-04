#!/usr/bin/env bash
# scripts/build-zip.sh — Упаковка landing-system в ZIP для раздачи
# Usage: bash scripts/build-zip.sh [output-dir]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${1:-$REPO_ROOT}"
ZIP_NAME="landing-system.zip"
ZIP_PATH="$OUTPUT_DIR/$ZIP_NAME"

echo "=== Landing System Builder ==="
echo "Репо: $REPO_ROOT"
echo "Архив: $ZIP_PATH"
echo ""

# Удалить старый архив если есть
[ -f "$ZIP_PATH" ] && rm "$ZIP_PATH"

cd "$(dirname "$REPO_ROOT")"
FOLDER="$(basename "$REPO_ROOT")"

zip -r "$ZIP_PATH" "$FOLDER" \
  --exclude "$FOLDER/.git/*" \
  --exclude "$FOLDER/.env" \
  --exclude "$FOLDER/.DS_Store" \
  --exclude "$FOLDER/**/.DS_Store" \
  --exclude "$FOLDER/**/__pycache__/*" \
  --exclude "$FOLDER/**/*.pyc" \
  --exclude "$FOLDER/**/*.pyo" \
  --exclude "$FOLDER/**/.pytest_cache/*" \
  --exclude "$FOLDER/.pytest_cache/*" \
  --exclude "$FOLDER/**/node_modules/*" \
  --exclude "$FOLDER/*.zip" \
  -q

SIZE="$(du -sh "$ZIP_PATH" | cut -f1)"
echo "✅ Готово: $ZIP_PATH ($SIZE)"
echo ""
echo "Содержимое:"
zip -sf "$ZIP_PATH" | head -30
echo "..."
echo ""
echo "Установка (ученику):"
echo "  1. Распакуй архив"
echo "  2. cd landing-system"
echo "  3. cp .env.example .env  # заполни ключи"
echo "  4. bash scripts/check-deps.sh"
echo "  5. В Claude Code: /landing-new my-project"
