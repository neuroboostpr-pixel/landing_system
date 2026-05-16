#!/bin/bash
# scripts/verify-visual-qa.sh — для stage-gates soft_check
set -uo pipefail
PROJECT="${1:?ERROR: project required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/verify_visual_qa.py" "$PROJECT"
