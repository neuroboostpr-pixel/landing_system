#!/bin/bash
# scripts/lib/python-cmd.sh
# Cross-platform Python detection. Source from other scripts:
#
#   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
#   REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
#   . "$REPO_ROOT/scripts/lib/python-cmd.sh"
#   "$PYTHON_CMD" -m scripts.wiki.compile ...
#
# On Linux/macOS PYTHON_CMD=python3. On Windows where `python3` is the
# Microsoft Store stub (exits non-zero with no output), falls back to
# `python` if it's Python 3.x. Exports PYTHON_CMD.

_detect_python() {
    # Try python3 first (canonical on Linux/macOS).
    if command -v python3 >/dev/null 2>&1; then
        # Verify it actually runs (catches MS Store stub on Windows).
        if python3 -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
            echo "python3"
            return 0
        fi
    fi
    # Fallback to `python` if it's Python 3.x.
    if command -v python >/dev/null 2>&1; then
        local ver
        ver=$(python -c "import sys; print(sys.version_info[0])" 2>/dev/null || echo "")
        if [ "$ver" = "3" ]; then
            echo "python"
            return 0
        fi
    fi
    # Last resort — `py` launcher on Windows.
    if command -v py >/dev/null 2>&1; then
        if py -3 -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
            echo "py -3"
            return 0
        fi
    fi
    return 1
}

if ! PYTHON_CMD=$(_detect_python); then
    echo "❌ Python 3 не найден. Установи python3 или python (>=3.8)." >&2
    return 1 2>/dev/null || exit 1
fi
export PYTHON_CMD
