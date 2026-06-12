#!/bin/bash
# scripts/hooks/run-stage-gate.sh
# Cross-platform wrapper for the stage-gate PreToolUse hook. Resolves
# Python via scripts/lib/python-cmd.sh. Invoked from .claude/settings.json.

set -uo pipefail

if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
    REPO_ROOT="$CLAUDE_PROJECT_DIR"
else
    REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
fi

# shellcheck source=../lib/python-cmd.sh
. "$REPO_ROOT/scripts/lib/python-cmd.sh"

exec $PYTHON_CMD "$REPO_ROOT/scripts/hooks/enforce_stage_gate.py"
