#!/usr/bin/env bash
# test-smoke-rest.sh — verify REST /wp-json/landing/v1/lead works on live Beget.
# Reads <project>/.landing-state.yaml::audience_segments to know which subsites to test.
# Usage: bash test-smoke-rest.sh <project-dir>

set -euo pipefail

# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../scripts/lib/python-cmd.sh"
PROJECT="${1:?Usage: test-smoke-rest.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"

[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }
[ -f "$PROJECT/.landing-state.yaml" ] || { echo "ERROR: $PROJECT/.landing-state.yaml not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${ROOT_DOMAIN:?}"

PY=python; command -v $PYTHON_CMD >/dev/null 2>&1 && $PYTHON_CMD -c '' >/dev/null 2>&1 && PY=$PYTHON_CMD

URLS=$("$PY" -c "
import yaml
d = yaml.safe_load(open('$PROJECT/.landing-state.yaml', encoding='utf-8'))
print('http://${ROOT_DOMAIN}')
for s in (d.get('audience_segments') or []):
    print('http://' + s['host'])
")

FAIL=0
for url in $URLS; do
    echo "▶ Testing REST on $url"
    code=$(curl -s -o /tmp/lead-smoke-resp.json -w '%{http_code}' --max-time 15 \
        -X POST "$url/wp-json/landing/v1/lead" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --data "name=SmokeTest&phone=%2B70000000000&email=smoke%40test.local&source_block=smoke" || echo "000")

    if [ "$code" = "200" ]; then
        echo "  ✅ HTTP 200 — response: $(cat /tmp/lead-smoke-resp.json)"
    else
        echo "  ❌ HTTP $code — response: $(cat /tmp/lead-smoke-resp.json 2>/dev/null || echo '(no body)')"
        FAIL=1
    fi
done

rm -f /tmp/lead-smoke-resp.json
exit $FAIL
