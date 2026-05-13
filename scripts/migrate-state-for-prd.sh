#!/usr/bin/env bash
# migrate-state-for-prd.sh — add new PR-D stages to existing .landing-state.yaml.
#
# Usage: bash migrate-state-for-prd.sh <path-to-.landing-state.yaml>
# Idempotent: existing stages preserved, only missing ones added (status=locked).
# Bumps schema_version to 2.

set -euo pipefail

STATE="${1:?ERROR: state.yaml path required}"
[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 2; }

python3 - "$STATE" <<'PYEOF'
import sys
import re
from pathlib import Path

NEW_STAGES = [
    "07a_prototype", "07b_wireframe", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
]

p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")

added = []
for sid in NEW_STAGES:
    # Check if stage already present (quoted or unquoted key)
    if re.search(r'["\']?' + re.escape(sid) + r'["\']?\s*:', text):
        continue
    # Append new stage line in inline block style with quoted key
    text = text.rstrip('\n') + f'\n  "{sid}":           {{status: locked, timestamp: ""}}\n'
    added.append(sid)

# Bump schema_version to 2 if not already
text = re.sub(r'^schema_version:\s*1\s*$', 'schema_version: 2', text, flags=re.MULTILINE)
# Ensure schema_version: 2 if already 2 (idempotent, no-op)

p.write_text(text, encoding="utf-8")

if added:
    print(f"Added {len(added)} stages: {', '.join(added)}")
else:
    print("Already migrated; no changes")
PYEOF
