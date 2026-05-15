#!/bin/bash
# skills/photo-curation/scripts/codex-process-photo.sh
# Обработка одного фото через codex image_gen.
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
# Выход: processed.jpg в указанном пути

set -uo pipefail

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
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

[ -z "$INPUT" ] || [ -z "$OUTPUT" ] && { echo "ERROR: --input and --output required" >&2; exit 2; }
[ -f "$INPUT" ] || { echo "ERROR: $INPUT not found" >&2; exit 2; }

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
PROMPT_TEMPLATE="$(dirname "$0")/../templates/codex-photo-prompt.md"

# Подготовка промпта (подстановка)
PROMPT=$(cat "$PROMPT_TEMPLATE" | sed \
    -e "s|{RATIO}|${RATIO:-16:9}|g" \
    -e "s|{BRAND_COLOR}|${BRAND_COLOR:-#000000}|g" \
    -e "s|{NICHE}|${NICHE:-generic}|g" \
    -e "s|{REGION}|${REGION:-global}|g")

# codex CLI вызов
if ! command -v codex >/dev/null 2>&1; then
    echo "ERROR: codex CLI not installed. Run: bash scripts/install-codex.sh" >&2
    exit 3
fi

# image_gen режим codex
codex exec image_gen \
    --image "$INPUT" \
    --prompt "$PROMPT" \
    --output "$OUTPUT" \
    2>&1 | tail -5

if [ ! -f "$OUTPUT" ]; then
    echo "ERROR: codex didn't produce $OUTPUT" >&2
    exit 1
fi

echo "✅ Processed: $OUTPUT ($(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT") bytes)"
