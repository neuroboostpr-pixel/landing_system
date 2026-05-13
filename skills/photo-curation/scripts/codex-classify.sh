#!/usr/bin/env bash
# codex-classify.sh — classify ONE photo, append entry to catalog.yaml.
#
# Usage:
#   bash codex-classify.sh <project_dir> <photo_path>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
PHOTO="${2:?ERROR: photo path required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/classify-prompt.md"

# Extract Prompt body from template, write to temp file
RAW_FILE="$(mktemp)"
python3 - "$TEMPLATE" "$RAW_FILE" <<'PYEOF'
import re, sys
template_path, raw_out = sys.argv[1], sys.argv[2]
text = open(template_path).read()
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: classify-prompt.md missing Prompt body section")
with open(raw_out, "w") as f:
    f.write(m.group(1))
PYEOF

# Render placeholders (NICHE, AUDIENCE, VISUAL_STYLE, BRAND_PRIMARY, etc.)
PROMPT_FILE="$(mktemp)"
python3 "$SCRIPT_DIR/render-prompt.py" "$RAW_FILE" "$PROJECT_DIR" > "$PROMPT_FILE"
rm -f "$RAW_FILE"

# Call codex with image input; capture response to temp file
RESPONSE_FILE="$(mktemp)"
bash "$SCRIPT_DIR/call-codex.sh" "$PROJECT_DIR" "classify" "$PROMPT_FILE" --image "$PHOTO" > "$RESPONSE_FILE"
rm -f "$PROMPT_FILE"

# Parse YAML response and append/update catalog entry
PHOTO_ID=$(basename "$PHOTO" | sed 's/\.[^.]*$//')
CATALOG="$PROJECT_DIR/07c_PHOTOS/catalog.yaml"

python3 - "$RESPONSE_FILE" "$CATALOG" "$PHOTO_ID" <<'PYEOF'
import sys, yaml
from pathlib import Path

response_path, catalog_path_str, photo_id = sys.argv[1], sys.argv[2], sys.argv[3]
catalog_path = Path(catalog_path_str)
catalog = yaml.safe_load(catalog_path.read_text()) if catalog_path.exists() else {"photos": []}
if catalog is None:
    catalog = {"photos": []}
catalog.setdefault("photos", [])

try:
    parsed = yaml.safe_load(open(response_path).read())
    if not isinstance(parsed, dict):
        raise yaml.YAMLError("root not a dict")
except yaml.YAMLError as e:
    print(f"WARN: invalid YAML from codex: {e}. Tagging as unclassified.", file=sys.stderr)
    parsed = {"tags": ["unclassified"], "caption": "", "face_count": 0,
              "composition": "object-only", "usable_ratios": [], "brand_compatible": "maybe",
              "notes": "codex YAML parse failed"}

existing = [p for p in catalog["photos"] if p.get("id") == photo_id]
if existing:
    existing[0].update(parsed)
    existing[0]["tag_source"] = "ai_classify"
else:
    parsed["id"] = photo_id
    parsed["tag_source"] = "ai_classify"
    catalog["photos"].append(parsed)

catalog_path.write_text(yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False))
print(f"OK: classified {photo_id}")
PYEOF
rm -f "$RESPONSE_FILE"
