#!/bin/bash
# scripts/wiki/hooks/run-hook.sh <hook-name>
# Cross-platform wrapper for wiki session hooks. Resolves Python via
# scripts/lib/python-cmd.sh and runs the named hook from this directory.
# Used from .claude/settings.json hooks.

set -uo pipefail

HOOK_NAME="${1:-}"
if [ -z "$HOOK_NAME" ]; then
    echo "usage: run-hook.sh <hook-name>" >&2
    exit 2
fi

# CLAUDE_PROJECT_DIR is set by Claude Code; fall back to script-relative
# resolution when invoked outside Claude Code.
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    REPO_ROOT="$CLAUDE_PROJECT_DIR"
else
    REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
fi

# shellcheck source=../../lib/python-cmd.sh
. "$REPO_ROOT/scripts/lib/python-cmd.sh"

exec $PYTHON_CMD "$REPO_ROOT/scripts/wiki/hooks/${HOOK_NAME}.py"
