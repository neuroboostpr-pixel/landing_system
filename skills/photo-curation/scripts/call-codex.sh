#!/usr/bin/env bash
# call-codex.sh — shared wrapper for codex exec with retry + logging.
#
# Usage:
#   bash call-codex.sh <project_dir> <stage> <prompt_file> [--image <path>]...
#
# Outputs codex stdout to stdout. Logs full prompt + response to:
#   <project_dir>/07c_PHOTOS/.logs/YYYY-MM-DD_HHMMSS_<stage>.log

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
STAGE="${2:?ERROR: stage name required (classify|match|generate)}"
PROMPT_FILE="${3:?ERROR: prompt_file required}"
shift 3

IMAGE_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --image)
            IMAGE_ARGS+=("--image" "$2")
            shift 2
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

CODEX_BIN="${CODEX_BIN:-codex}"
LOGS_DIR="$PROJECT_DIR/07c_PHOTOS/.logs"
mkdir -p "$LOGS_DIR"
TS="$(date +%Y-%m-%d_%H%M%S)"
LOG="$LOGS_DIR/${TS}_${STAGE}.log"

PROMPT="$(cat "$PROMPT_FILE")"

{
    echo "=== STAGE: $STAGE ==="
    echo "=== TIMESTAMP: $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%dT%H:%M:%SZ) ==="
    echo "=== IMAGE_ARGS: ${IMAGE_ARGS[*]:-<none>} ==="
    echo "=== PROMPT ==="
    echo "$PROMPT"
    echo "=== RESPONSE ==="
} > "$LOG"

# Build codex args
CODEX_ARGS=("exec" "--skip-git-repo-check")
if [ ${#IMAGE_ARGS[@]} -gt 0 ]; then
    CODEX_ARGS+=("${IMAGE_ARGS[@]}")
fi

# Retry up to 2 times for transient failures
RC=0
for attempt in 1 2; do
    if RESPONSE=$("$CODEX_BIN" "${CODEX_ARGS[@]}" "$PROMPT" 2>>"$LOG"); then
        echo "$RESPONSE" >> "$LOG"
        echo "$RESPONSE"
        exit 0
    fi
    RC=$?
    echo "WARN: codex exec attempt $attempt failed (rc=$RC). Retrying..." >&2
    sleep 2
done

echo "ERROR: codex exec failed after 2 attempts. See $LOG" >&2
exit $RC
