#!/usr/bin/env bash
# skills/photo-curation/scripts/codex-process-photo.sh
# Обработка одного фото через `codex exec` (паттерн из paralaximus-codex).
#
# Codex CLI принимает промпт через stdin + reference image через -i.
# Результат пишется в ~/.codex/generated_images/<session-uuid>/*.png — мы сами
# копируем самый свежий PNG в --output.
#
# Использование:
#   codex-process-photo.sh \
#     --input <orig.jpg> \
#     --output <processed.jpg> \
#     --slot-ratio "16:9" \
#     --brand-color "#1a1a1a" \
#     --niche "premium-auto" \
#     --region "Dubai"
#
# Зависит от:
#   - codex CLI (codex login сделан)
#   - templates/codex-photo-prompt.md (промпт-шаблон)

set -euo pipefail

INPUT=""
OUTPUT=""
RATIO=""
BRAND_COLOR=""
NICHE=""
REGION=""

while [ $# -gt 0 ]; do
    case "$1" in
        --input) INPUT="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --slot-ratio) RATIO="$2"; shift 2 ;;
        --brand-color) BRAND_COLOR="$2"; shift 2 ;;
        --niche) NICHE="$2"; shift 2 ;;
        --region) REGION="$2"; shift 2 ;;
        *) echo "ERROR: unknown arg $1" >&2; exit 2 ;;
    esac
done

[ -n "$INPUT" ]  || { echo "ERROR: --input required" >&2; exit 2; }
[ -n "$OUTPUT" ] || { echo "ERROR: --output required" >&2; exit 2; }
[ -f "$INPUT" ]  || { echo "ERROR: $INPUT not found" >&2; exit 2; }

PROMPT_TEMPLATE="$(dirname "$0")/../templates/codex-photo-prompt.md"
[ -f "$PROMPT_TEMPLATE" ] || { echo "ERROR: prompt template missing: $PROMPT_TEMPLATE" >&2; exit 2; }

# codex может быть установлен в нестандартное место — добавим типичные пути в PATH
export PATH="$HOME/.local/node-current/bin:$HOME/.local/bin:$PATH"

if ! command -v codex >/dev/null 2>&1; then
    echo "ERROR: codex CLI не найден в PATH" >&2
    echo "       Проверь: ls ~/.local/node-current/bin/codex" >&2
    echo "       Логин:   codex login" >&2
    exit 3
fi

# Подготовка промпта — подстановка переменных в шаблон
PROMPT=$(sed \
    -e "s|{RATIO}|${RATIO:-16:9}|g" \
    -e "s|{BRAND_COLOR}|${BRAND_COLOR:-#000000}|g" \
    -e "s|{NICHE}|${NICHE:-generic}|g" \
    -e "s|{REGION}|${REGION:-global}|g" \
    "$PROMPT_TEMPLATE")

# Snapshot существующих codex-сессий, чтобы потом найти НОВУЮ
TMP_BEFORE="$(mktemp)"
ls -1 "$HOME/.codex/generated_images/" 2>/dev/null | sort > "$TMP_BEFORE" || true

echo "→ Вызываю codex exec для обработки фото..." >&2

# Паттерн идентичный paralaximus-codex/scripts/generate-atlas.sh:
# - промпт через stdin (printf | codex exec ... -)
# - reference image через -i
# - --skip-git-repo-check чтобы codex не требовал git-репо
if ! printf '%s' "$PROMPT" | codex exec --skip-git-repo-check -i "$INPUT" - >&2; then
    rc=$?
    echo "ERROR: codex exec exited with $rc" >&2
    rm -f "$TMP_BEFORE"
    exit "$rc"
fi

# Найти новую session-папку, появившуюся в этот прогон
TMP_AFTER="$(mktemp)"
ls -1 "$HOME/.codex/generated_images/" 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER"

if [ -z "$NEW_DIR" ]; then
    echo "WARN: новая session-папка не найдена — беру самую свежую существующую" >&2
    NEW_DIR="$(ls -1t "$HOME/.codex/generated_images/" 2>/dev/null | head -1)"
fi

[ -n "$NEW_DIR" ] || { echo "ERROR: codex generated_images dir пуст" >&2; exit 3; }

SRC_DIR="$HOME/.codex/generated_images/$NEW_DIR"
SRC_PNG="$(ls -1t "$SRC_DIR"/*.png 2>/dev/null | head -1 || true)"

[ -n "$SRC_PNG" ] || { echo "ERROR: PNG не появился в $SRC_DIR" >&2; exit 4; }

mkdir -p "$(dirname "$OUTPUT")"
cp "$SRC_PNG" "$OUTPUT"

SIZE_KB=$(( $(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null || echo 0) / 1024 ))
echo "✅ Processed: $OUTPUT (${SIZE_KB} KB)" >&2
echo "   Источник:  $SRC_PNG" >&2
