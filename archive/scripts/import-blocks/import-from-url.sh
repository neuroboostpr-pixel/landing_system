#!/usr/bin/env bash
# scripts/import-blocks/import-from-url.sh
# Pipeline: URL → screenshot → codex analysis → generated blocks → block-library/
#
# Usage:
#   import-from-url.sh <url> [niche]
set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/python-cmd.sh
. "$__SCRIPT_DIR__/../lib/python-cmd.sh"
URL="${1:?ERROR: URL required}"
NICHE="${2:-generic}"

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HASH=$(printf '%s' "$URL" | shasum -a 256 | head -c 12)
WORK_DIR="$REPO_ROOT/.import-blocks-work/$HASH"
mkdir -p "$WORK_DIR/screenshots"

echo "[1/5] Скачиваю $URL..."

if [[ "$URL" == *.pdf ]]; then
    curl -sL "$URL" -o "$WORK_DIR/source.pdf"
    if command -v pdftoppm >/dev/null 2>&1; then
        pdftoppm -r 110 -png "$WORK_DIR/source.pdf" "$WORK_DIR/screenshots/page"
    elif command -v pdfimages >/dev/null 2>&1; then
        pdfimages -png "$WORK_DIR/source.pdf" "$WORK_DIR/screenshots/page"
    else
        echo "ERROR: ни pdftoppm, ни pdfimages не установлены" >&2
        exit 5
    fi
else
    $PYTHON_CMD "$(dirname "$0")/take-page-screenshot.py" "$URL" --out "$WORK_DIR/screenshots/"
fi

echo "Скриншоты в $WORK_DIR/screenshots/"
shopt -s nullglob
SCREENSHOTS=( "$WORK_DIR/screenshots"/*.png )
shopt -u nullglob
[ ${#SCREENSHOTS[@]} -gt 0 ] || { echo "ERROR: нет скриншотов" >&2; exit 2; }

echo "[2/5] Анализирую структуру через codex..."
MAIN_SCREENSHOT="${SCREENSHOTS[0]}"

bash "$(dirname "$0")/codex-analyze-structure.sh" "$MAIN_SCREENSHOT" \
    > "$WORK_DIR/structure.json" 2>"$WORK_DIR/analysis.log" || {
    echo "ERROR: codex analysis failed. См. $WORK_DIR/analysis.log" >&2
    exit 3
}

$PYTHON_CMD -c "import json; json.load(open('$WORK_DIR/structure.json'))" 2>/dev/null || {
    echo "ERROR: codex вернул не-JSON. См. $WORK_DIR/structure.json" >&2
    exit 4
}

BLOCK_COUNT=$($PYTHON_CMD -c "import json; print(len(json.load(open('$WORK_DIR/structure.json')).get('blocks', [])))")
echo "   Найдено блоков: $BLOCK_COUNT"

echo "[3/5] Генерирую универсальные HTML+CSS для блоков..."
$PYTHON_CMD "$(dirname "$0")/generate-blocks.py" \
    --structure "$WORK_DIR/structure.json" \
    --screenshot "$MAIN_SCREENSHOT" \
    --niche "$NICHE" \
    --source-url "$URL" \
    --out "$REPO_ROOT/block-library/" \
    --work-dir "$WORK_DIR/"

echo "[4/5] Обновляю catalog.yaml..."
$PYTHON_CMD "$(dirname "$0")/update-catalog.py" \
    --library "$REPO_ROOT/block-library/" \
    --added-from "$WORK_DIR/added-blocks.json"

echo "[5/5] Done. Импортировано блоков из $URL"
$PYTHON_CMD -m json.tool "$WORK_DIR/added-blocks.json" 2>/dev/null | head -30 || cat "$WORK_DIR/added-blocks.json"
echo ""
echo "Работа сохранена в: $WORK_DIR"
