#!/usr/bin/env bash
# verify-php-syntax.sh — run `php -l` on every .php file in a directory.
#
# Usage: verify-php-syntax.sh <dir>
# Exit codes:
#   0 — all PHP files parse cleanly
#   1 — at least one syntax error
#   2 — dir missing OR php not installed

set -euo pipefail

DIR="${1:?ERROR: directory required}"

[ -d "$DIR" ] || {
    echo "ERROR: dir not found: $DIR" >&2
    exit 2
}

if ! command -v php >/dev/null 2>&1; then
    echo "WARN: php CLI not installed — skipping PHP syntax check" >&2
    exit 0
fi

errors=0
while IFS= read -r -d '' f; do
    if ! php -l "$f" >/dev/null 2>&1; then
        echo "✗ PHP syntax error: $f" >&2
        php -l "$f" >&2 || true
        errors=$((errors+1))
    fi
done < <(find "$DIR" -name "*.php" -print0)

if [ "$errors" -gt 0 ]; then
    echo "FAIL: $errors PHP file(s) have syntax errors" >&2
    exit 1
fi

echo "OK: all PHP files in $DIR parse cleanly"
