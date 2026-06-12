#!/usr/bin/env bash
# codex-review-screenshot.sh — отправляет скриншот в codex, возвращает JSON.
#
# Паттерн — тот же что в paralaximus-codex/generate-atlas.sh и
# photo-curation/codex-process-photo.sh: stdin prompt + -i image,
# результат — текстовый ответ codex (последняя сессия в transcripts).
#
# Использование:
#   codex-review-screenshot.sh <screenshot.png> > review.json

set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../scripts/lib/python-cmd.sh"
SCREENSHOT="${1:?ERROR: screenshot path required}"
[ -f "$SCREENSHOT" ] || { echo "ERROR: $SCREENSHOT not found" >&2; exit 2; }

PROMPT_TEMPLATE="$(dirname "$0")/../templates/review-prompt.md"
[ -f "$PROMPT_TEMPLATE" ] || { echo "ERROR: $PROMPT_TEMPLATE not found" >&2; exit 2; }

export PATH="$HOME/.local/node-current/bin:$HOME/.local/bin:$PATH"
if ! command -v codex >/dev/null 2>&1; then
    echo "ERROR: codex CLI не найден" >&2
    exit 3
fi

PROMPT=$(cat "$PROMPT_TEMPLATE")

# codex exec возвращает текст ответа в stdout
# (отличается от generate-atlas.sh где смотрим на generated_images/ —
#  здесь нам нужен текстовый JSON, а не картинка)
RESPONSE=$(printf '%s' "$PROMPT" | codex exec --skip-git-repo-check -i "$SCREENSHOT" - 2>/dev/null)

# Извлечь JSON блок из ответа (codex может обернуть в ```json ... ```)
JSON=$(echo "$RESPONSE" | sed -n '/^```json/,/^```/p' | sed '1d;$d')
if [ -z "$JSON" ]; then
    # Если нет ```json``` обёртки, попробовать взять весь ответ
    JSON="$RESPONSE"
fi

# Валидация что это JSON
if ! echo "$JSON" | $PYTHON_CMD -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    echo "ERROR: codex вернул не-JSON ответ" >&2
    echo "Raw response:" >&2
    echo "$RESPONSE" >&2
    exit 4
fi

echo "$JSON"
