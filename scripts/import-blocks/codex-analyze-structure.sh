#!/usr/bin/env bash
# Codex CLI vision → JSON со структурой блоков скриншота.
set -euo pipefail
SCREENSHOT="${1:?ERROR: screenshot required}"

[ -f "$SCREENSHOT" ] || { echo "ERROR: screenshot not found: $SCREENSHOT" >&2; exit 2; }

PROMPT_TEMPLATE="$(dirname "$0")/templates/structure-analysis-prompt.md"
[ -f "$PROMPT_TEMPLATE" ] || { echo "ERROR: template not found: $PROMPT_TEMPLATE" >&2; exit 3; }

if [ -z "${CODEX_BIN:-}" ]; then
    export PATH="$HOME/.local/node-current/bin:$HOME/.local/bin:$PATH"
fi
CODEX_BIN="${CODEX_BIN:-codex}"
command -v "$CODEX_BIN" >/dev/null 2>&1 || { echo "ERROR: codex CLI not found ($CODEX_BIN)" >&2; exit 4; }

PROMPT="$(cat "$PROMPT_TEMPLATE")"

RESPONSE=$(printf '%s' "$PROMPT" | "$CODEX_BIN" exec --skip-git-repo-check -i "$SCREENSHOT" - 2>/dev/null)

# Достаём fenced JSON если он есть, иначе считаем весь ответ JSON-ом
JSON=$(echo "$RESPONSE" | sed -n '/^```json/,/^```/p' | sed '1d;$d')
[ -n "$JSON" ] || JSON="$RESPONSE"

printf '%s\n' "$JSON"
