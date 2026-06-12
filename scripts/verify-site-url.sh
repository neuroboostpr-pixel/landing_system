#!/usr/bin/env bash
# verify-site-url.sh — curl HEAD on deployed URL from .landing-state.yaml.
#
# Usage: verify-site-url.sh <path-to-.landing-state.yaml>
# Exit codes:
#   0 — URL returns 2xx
#   1 — URL not reachable or non-2xx
#   2 — state.yaml missing or no deploy_url

set -euo pipefail

STATE="${1:?ERROR: state.yaml path required}"

[ -f "$STATE" ] || {
    echo "ERROR: state.yaml not found at $STATE" >&2
    exit 2
}

URL="$(python - "$STATE" <<'PYEOF'
import yaml, sys
data = yaml.safe_load(open(sys.argv[1]).read())
stage = data.get('stages', {}).get('09_deploy', {})
url = stage.get('deploy_url', '') if isinstance(stage, dict) else ''
print(url)
PYEOF
)"

if [ -z "$URL" ]; then
    echo "ERROR: no deploy_url recorded in state.yaml:stages.09_deploy" >&2
    exit 2
fi

if curl -fsSI -L --max-time 10 "$URL" >/dev/null 2>&1; then
    echo "OK: $URL is accessible"
    exit 0
else
    echo "FAIL: $URL not reachable or returned non-2xx" >&2
    exit 1
fi
