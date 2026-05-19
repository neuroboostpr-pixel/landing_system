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
    # Default to empty JSON object. NOTE: ${2:-{}} would expand wrong —
    # bash closes the expansion at the first `}`, appending the second `}`
    # to the value. Use explicit conditional to avoid this footgun.
    local input_data="${2-}"
    [ -z "$input_data" ] && input_data='{}'
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

# --- Subdomain helpers ----------------------------------------------------

beget_subdomain_exists() {
    # beget_subdomain_exists <fqdn> — exit 0 if subdomain found in account
    local fqdn="$1"
    local resp
    resp=$(beget_api "domain/getSubdomainList")
    export FQDN="$fqdn"
    local rc=0
    printf '%s' "$resp" | python -c '
import sys, json, os
fqdn = os.environ["FQDN"]
try:
    d = json.load(sys.stdin)
    found = any(x.get("fqdn") == fqdn for x in d.get("answer", {}).get("result", []))
    sys.exit(0 if found else 1)
except Exception:
    sys.exit(1)
' || rc=$?
    unset FQDN
    return $rc
}

beget_subdomain_id() {
    # beget_subdomain_id <fqdn> — print numeric id; exit 1 if not found
    local fqdn="$1"
    local resp
    resp=$(beget_api "domain/getSubdomainList")
    export FQDN="$fqdn"
    local rc=0
    printf '%s' "$resp" | python -c '
import sys, json, os
fqdn = os.environ["FQDN"]
try:
    d = json.load(sys.stdin)
    for x in d.get("answer", {}).get("result", []):
        if x.get("fqdn") == fqdn:
            print(x["id"]); sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
' || rc=$?
    unset FQDN
    return $rc
}

beget_subdomain_add() {
    # beget_subdomain_add <subdomain> <root_domain_id> — print new subdomain id
    local sub="$1" root_id="$2"
    [[ "$sub" =~ ^[a-zA-Z0-9*_-]+$ ]] || {
        echo "beget_subdomain_add: invalid subdomain '$sub' (must match [a-zA-Z0-9*_-]+)" >&2
        return 1
    }
    [[ "$root_id" =~ ^[0-9]+$ ]] || {
        echo "beget_subdomain_add: root_id must be numeric, got '$root_id'" >&2
        return 1
    }
    local resp
    resp=$(beget_api "domain/addSubdomainVirtual" "{\"subdomain\":\"$sub\",\"domain_id\":$root_id}")
    if beget_ok "$resp"; then
        printf '%s' "$resp" | python -c "
import sys, json
print(json.load(sys.stdin)['answer']['result'])
"
        return 0
    fi
    echo "beget_subdomain_add failed: $(beget_error_text "$resp")" >&2
    return 1
}

# --- Site/domain linking --------------------------------------------------

beget_site_link() {
    # beget_site_link <domain_id> <site_id> — exit 0 on success
    local dom_id="$1" site_id="$2"
    local resp
    resp=$(beget_api "site/linkDomain" "{\"domain_id\":$dom_id,\"site_id\":$site_id}")
    beget_ok "$resp" || {
        echo "beget_site_link failed: $(beget_error_text "$resp")" >&2
        return 1
    }
}

# --- PHP version ---------------------------------------------------------

beget_set_php() {
    # beget_set_php <full_fqdn> <version> — e.g. "alpha.ailexi.ru" "8.3"
    local fqdn="$1" version="$2"
    [[ "$fqdn" =~ ^[a-zA-Z0-9.*_-]+$ ]] || {
        echo "beget_set_php: invalid fqdn '$fqdn'" >&2
        return 1
    }
    [[ "$version" =~ ^[0-9]+\.[0-9]+$ ]] || {
        echo "beget_set_php: version must look like '8.3', got '$version'" >&2
        return 1
    }
    local resp
    resp=$(beget_api "domain/changePhpVersion" "{\"full_fqdn\":\"$fqdn\",\"php_version\":\"$version\"}")
    beget_ok "$resp" || {
        echo "beget_set_php failed: $(beget_error_text "$resp")" >&2
        return 1
    }
}
