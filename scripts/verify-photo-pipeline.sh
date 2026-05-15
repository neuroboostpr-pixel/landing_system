#!/bin/bash
# scripts/verify-photo-pipeline.sh
set -uo pipefail
PROJECT="${1:?ERROR: project path required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/verify_photo_pipeline.py" "$PROJECT"
