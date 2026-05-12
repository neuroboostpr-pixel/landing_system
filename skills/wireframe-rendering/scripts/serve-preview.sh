#!/usr/bin/env bash
# Optional helper — serves wireframe.html over http://localhost:8000
# Useful when file:// breaks iframe sandboxing.
#
# Usage: serve-preview.sh <project>/07a_WIREFRAME/

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <project>/07a_WIREFRAME/" >&2
  exit 2
fi

DIR="$1"
PORT="${PORT:-8000}"

if [ ! -f "$DIR/wireframe.html" ]; then
  echo "ERROR: $DIR/wireframe.html not found" >&2
  exit 1
fi

echo "Serving $DIR at http://localhost:$PORT/wireframe.html"
echo "Press Ctrl+C to stop."
cd "$DIR"
exec python3 -m http.server "$PORT"
