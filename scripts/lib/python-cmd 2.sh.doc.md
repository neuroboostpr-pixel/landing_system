---
type: script
name: python-cmd 2
language: bash
sources: ["scripts/lib/python-cmd 2.sh"]
updated: 2026-05-18
---

# python-cmd 2.sh

scripts/lib/python-cmd.sh
Cross-platform Python detection. Source from other scripts:

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
. "$REPO_ROOT/scripts/lib/python-cmd.sh"
"$PYTHON_CMD" -m scripts.wiki.compile ...

On Linux/macOS PYTHON_CMD=python3. On Windows where `python3` is the
Microsoft Store stub (exits non-zero with no output), falls back to
`python` if it's Python 3.x. Exports PYTHON_CMD.

## Источник

- `scripts/lib/python-cmd 2.sh`
