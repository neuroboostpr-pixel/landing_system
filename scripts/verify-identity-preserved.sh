#!/bin/bash
# scripts/verify-identity-preserved.sh — для stage-gates 07f hard_check
set -uo pipefail

PROJECT="${1:?ERROR: project required}"
MANIFEST="$PROJECT/07c_PHOTOS/processed/manifest.json"

if [ ! -f "$MANIFEST" ]; then
    echo "✅ identity OK (нет processed manifest)"
    exit 0
fi

python3 - <<PYTHON
import json, sys
data = json.load(open("$MANIFEST"))
violations = [(k, v) for k, v in data.items() if isinstance(v, dict) and v.get("identity_violation")]
if not violations:
    print("✅ Identity сохранён для всех слотов")
    sys.exit(0)
print(f"❌ Identity violations ({len(violations)}):", file=sys.stderr)
for k, v in violations:
    d = v.get("distance", "?")
    t = v.get("threshold", "?")
    print(f"  - {k}: distance={d} > threshold={t}", file=sys.stderr)
sys.exit(1)
PYTHON
