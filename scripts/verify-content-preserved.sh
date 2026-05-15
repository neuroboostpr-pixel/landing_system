#!/bin/bash
# scripts/verify-content-preserved.sh — wrapper for verify_content_preserved.py
set -uo pipefail
PROJECT="${1:?ERROR: project path required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/verify_content_preserved.py" "$PROJECT"
