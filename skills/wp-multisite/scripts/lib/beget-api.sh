#!/usr/bin/env bash
# Production-ready Beget API wrapper.
# Required env: BEGET_API, BEGET_LOGIN, BEGET_PASSWD
# Validated on POC against ailexi.ru / esper21 account 2026-05-18.

beget_check_env() {
    if [[ -z "${BEGET_API:-}" || -z "${BEGET_LOGIN:-}" || -z "${BEGET_PASSWD:-}" ]]; then
        echo "beget-api: missing required env vars (BEGET_API, BEGET_LOGIN, BEGET_PASSWD)" >&2
        return 1
    fi
}

beget_api() {
    # beget_api <category/method> [input_data_json]
    beget_check_env || return 1
    local method="$1"
    local input_data="${2:-{}}"
    local response
    response=$(curl -s -X POST "${BEGET_API}/${method}" \
        --data-urlencode "login=${BEGET_LOGIN}" \
        --data-urlencode "passwd=${BEGET_PASSWD}" \
        --data-urlencode "input_format=json" \
        --data-urlencode "output_format=json" \
        --data-urlencode "input_data=${input_data}") || {
        local rc=$?
        echo "beget-api: curl failed with exit code $rc (network error or timeout)" >&2
        return $rc
    }
    printf '%s' "$response"
}

beget_ok() {
    # beget_ok <json_response> — exit 0 if both outer.status and answer.status == "success"
    local resp="$1"
    local outer inner
    outer=$(printf '%s' "$resp" | python -c 'import sys,json
try: print(json.load(sys.stdin).get("status",""))
except: print("")' 2>/dev/null)
    inner=$(printf '%s' "$resp" | python -c 'import sys,json
try: print(json.load(sys.stdin).get("answer",{}).get("status",""))
except: print("")' 2>/dev/null)
    [ "$outer" = "success" ] && [ "$inner" = "success" ]
}

beget_error_text() {
    # beget_error_text <json_response> — extract first error_text for diagnostics
    printf '%s' "$1" | python -c 'import sys,json
try:
    d=json.load(sys.stdin)
    errs=d.get("answer",{}).get("errors") or [{"error_text": d.get("error_text","unknown")}]
    print(errs[0].get("error_text","unknown"))
except: print("parse_error")' 2>/dev/null
}
