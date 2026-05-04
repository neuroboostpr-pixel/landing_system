#!/usr/bin/env bash
# scripts/setup-flag.sh — manage ~/.landing-system/setup_complete
set -euo pipefail

FLAG_DIR="$HOME/.landing-system"
FLAG_FILE="$FLAG_DIR/setup_complete"

cmd="${1:-}"

case "$cmd" in
    is_complete)
        [ -f "$FLAG_FILE" ] && exit 0 || exit 1
        ;;
    mark_complete)
        mkdir -p "$FLAG_DIR"
        date -u +"%Y-%m-%dT%H:%M:%SZ" > "$FLAG_FILE"
        ;;
    reset)
        rm -f "$FLAG_FILE"
        ;;
    timestamp)
        cat "$FLAG_FILE" 2>/dev/null || echo "not set"
        ;;
    *)
        echo "Usage: $0 {is_complete|mark_complete|reset|timestamp}" >&2
        exit 2
        ;;
esac
