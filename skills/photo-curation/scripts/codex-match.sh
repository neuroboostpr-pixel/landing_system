#!/usr/bin/env bash
# codex-match.sh — produce selections.draft.yaml from catalog + slots.
#
# Usage:
#   bash codex-match.sh <project_dir> <catalog_yaml> <slots_yaml>

set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../scripts/lib/python-cmd.sh"
PROJECT_DIR="${1:?ERROR: project_dir required}"
CATALOG="${2:?ERROR: catalog.yaml path required}"
SLOTS="${3:?ERROR: slots.yaml path required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/match-prompt.md"

# Extract prompt body and inline CATALOG_YAML + SLOTS_YAML, then render placeholders
RAW_FILE="$(mktemp)"
$PYTHON_CMD - "$TEMPLATE" "$CATALOG" "$SLOTS" "$RAW_FILE" <<'PYEOF'
import re, sys
template, catalog_path, slots_path, raw_out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
text = open(template).read()
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: match-prompt.md missing Prompt body section")
body = m.group(1)

catalog = open(catalog_path).read()
slots = open(slots_path).read()
body = body.replace("[CATALOG_YAML]", catalog)
body = body.replace("[SLOTS_YAML]", slots)

with open(raw_out, "w") as f:
    f.write(body)
PYEOF

PROMPT_FILE="$(mktemp)"
$PYTHON_CMD "$SCRIPT_DIR/render-prompt.py" "$RAW_FILE" "$PROJECT_DIR" > "$PROMPT_FILE"
rm -f "$RAW_FILE"

# Call codex (text-only, no image input); capture response to temp file
RESPONSE_FILE="$(mktemp)"
bash "$SCRIPT_DIR/call-codex.sh" "$PROJECT_DIR" "match" "$PROMPT_FILE" > "$RESPONSE_FILE"
rm -f "$PROMPT_FILE"

DRAFT="$PROJECT_DIR/07c_PHOTOS/selections.draft.yaml"
$PYTHON_CMD - "$RESPONSE_FILE" "$DRAFT" <<'PYEOF'
import sys, yaml
response_path, draft_path = sys.argv[1], sys.argv[2]
try:
    parsed = yaml.safe_load(open(response_path).read())
    assert isinstance(parsed, dict) and "slots" in parsed
except (yaml.YAMLError, AssertionError) as e:
    print(f"ERROR: matcher returned invalid YAML: {e}", file=sys.stderr)
    sys.exit(3)
with open(draft_path, "w") as f:
    yaml.safe_dump(parsed, f, allow_unicode=True, sort_keys=False)
print(f"OK: matched, draft at {draft_path}")
PYEOF
rm -f "$RESPONSE_FILE"
