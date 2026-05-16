#!/usr/bin/env bash
PR_J_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_dummy_jpg() {
    local path="$1"
    python3 -c "
from PIL import Image
Image.new('RGB', (800, 600), (100, 100, 100)).save('$path', 'JPEG', quality=85)
"
}

make_project_with_manifest() {
    local violations="$1"  # "" or "yes"
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07c_PHOTOS/processed"
    if [ "$violations" = "yes" ]; then
        cat > "$tmpdir/07c_PHOTOS/processed/manifest.json" <<JSON
{
  "hero-bg.jpg": {
    "slot": "hero-bg",
    "status": "reverted",
    "identity_violation": true,
    "distance": 14,
    "threshold": 12
  },
  "team-1.jpg": {
    "slot": "team-1",
    "status": "processed",
    "identity_violation": false,
    "distance": 3,
    "threshold": 5
  }
}
JSON
    else
        cat > "$tmpdir/07c_PHOTOS/processed/manifest.json" <<JSON
{
  "hero-bg.jpg": {
    "slot": "hero-bg",
    "status": "processed",
    "identity_violation": false,
    "distance": 4,
    "threshold": 12
  }
}
JSON
    fi
    echo "$tmpdir"
}
