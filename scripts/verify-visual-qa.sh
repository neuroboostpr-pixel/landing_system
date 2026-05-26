#!/bin/bash
# scripts/verify-visual-qa.sh — для stage-gates soft_check
set -uo pipefail

# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-cmd.sh
. "$__SCRIPT_DIR__/lib/python-cmd.sh"
PROJECT="${1:?ERROR: project required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec $PYTHON_CMD "$REPO_ROOT/scripts/verify_visual_qa.py" "$PROJECT"
