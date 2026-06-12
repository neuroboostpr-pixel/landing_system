#!/usr/bin/env bash
# Optional helper — serves wireframe.html over http://localhost:8000
# Useful when file:// breaks iframe sandboxing.
#
# Usage: serve-preview.sh <project>/07a_WIREFRAME/

set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../scripts/lib/python-cmd.sh"
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
exec $PYTHON_CMD -m http.server "$PORT"
