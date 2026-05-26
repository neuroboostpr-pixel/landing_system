#!/usr/bin/env bash
# acme.sh DNS API plugin for Beget Hosting (validated working on 2026-05-18)
#
# Validated:
#  - Wildcard cert for *.ailexi.ru — SUCCESS (TXT on _acme-challenge.ailexi.ru propagates)
#  - Per-subdomain cert for alpha.ailexi.ru via DNS-01 — FAILS
#    (TXT on _acme-challenge.alpha.ailexi.ru does NOT propagate, Beget treats
#    triple-level domain TXT as not under its DNS control)
#
# Required env (set once; acme.sh saves to ~/.acme.sh/account.conf):
#   export BEGET_Login="<your-account-login>"
#   export BEGET_Password='<API_password>'   # NOT main account password
#
# Usage:
#   ./acme.sh --issue --dns dns_beget -d <root>.ru -d '*.<root>.ru' --server letsencrypt
#
# For per-subdomain certs, use HTTP-01 instead:
#   ./acme.sh --issue --webroot ~/<root>.ru/public_html -d <sub>.<root>.ru --server letsencrypt
#
# Installation: copy this file to ~/.acme.sh/dnsapi/dns_beget.sh on Beget,
# then `chmod +x ~/.acme.sh/dnsapi/dns_beget.sh`.


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../scripts/lib/python-cmd.sh"
dns_beget_info='Beget Hosting (Russia)
Site: https://beget.com/
Docs: https://beget.com/en/kb/api/dns-administration-functions
'

BEGET_API="https://api.beget.com/api"

# Mapping root_domain → numeric domain_id. Used to create _acme-challenge subdomain.
# Extend this when adding new root domains; values from `domain/getList`.
_beget_root_domain_id() {
    case "$1" in
        ailexi.ru) echo 12513532 ;;
        ailexi.online) echo 13568994 ;;
        ailexi.store) echo 12513533 ;;
        *) _err "Unknown root domain $1 — extend _beget_root_domain_id()"; return 1 ;;
    esac
}

dns_beget_add() {
    fulldomain="$1"  # e.g. _acme-challenge.ailexi.ru
    txtvalue="$2"

    BEGET_Login="${BEGET_Login:-$(_readaccountconf_mutable BEGET_Login)}"
    BEGET_Password="${BEGET_Password:-$(_readaccountconf_mutable BEGET_Password)}"
    if [ -z "$BEGET_Login" ] || [ -z "$BEGET_Password" ]; then
        _err "BEGET_Login and BEGET_Password must be set"
        return 1
    fi
    _saveaccountconf_mutable BEGET_Login "$BEGET_Login"
    _saveaccountconf_mutable BEGET_Password "$BEGET_Password"

    root=$(echo "$fulldomain" | awk -F. '{print $(NF-1)"."$NF}')
    sub=$(echo "$fulldomain" | sed "s/\\.${root}\$//")

    _info "Beget: add TXT $fulldomain (sub=$sub, root=$root) = $txtvalue"

    # Ensure subdomain exists. Beget accepts underscore-prefix (_acme-challenge).
    root_id=$(_beget_root_domain_id "$root") || return 1
    sub_id=$(curl -s -X POST "$BEGET_API/domain/getSubdomainList" \
        --data-urlencode "login=$BEGET_Login" --data-urlencode "passwd=$BEGET_Password" \
        --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
        | $PYTHON_CMD -c "import sys,json; d=json.load(sys.stdin); [print(x['id']) for x in d['answer']['result'] if x['fqdn']=='$fulldomain']" | head -1)

    if [ -z "$sub_id" ]; then
        _info "Beget: creating subdomain $sub under $root (root_id=$root_id)"
        resp=$(curl -s -X POST "$BEGET_API/domain/addSubdomainVirtual" \
            --data-urlencode "login=$BEGET_Login" --data-urlencode "passwd=$BEGET_Password" \
            --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
            --data-urlencode "input_data={\"subdomain\":\"$sub\",\"domain_id\":$root_id}")
        if ! echo "$resp" | grep -q '"status":"success".*"status":"success"'; then
            _err "Beget: failed to create subdomain $sub: $resp"
            return 1
        fi
    fi

    # Fetch existing TXT records (might be empty for new subdomain)
    cur_resp=$(curl -s -X POST "$BEGET_API/dns/getData" \
        --data-urlencode "login=$BEGET_Login" --data-urlencode "passwd=$BEGET_Password" \
        --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
        --data-urlencode "input_data={\"fqdn\":\"$fulldomain\"}")

    cur_txts=$(echo "$cur_resp" | $PYTHON_CMD -c "
import sys, json
try:
    d = json.load(sys.stdin)
    res = d.get('answer', {}).get('result', {})
    recs = res.get('records', {}) if isinstance(res, dict) else {}
    txts = recs.get('TXT', []) or []
    out = [{'priority': 10, 'value': t.get('txtdata') or t.get('value')} for t in txts if t.get('txtdata') or t.get('value')]
    print(json.dumps(out))
except Exception:
    print('[]')
")

    # Append new TXT and PUT back via dns/changeRecords (full replace)
    new_records=$($PYTHON_CMD -c "
import json
existing = json.loads('''$cur_txts''')
existing.append({'priority': 10, 'value': '$txtvalue'})
print(json.dumps({'fqdn': '$fulldomain', 'records': {'TXT': existing}}))
")

    resp=$(curl -s -X POST "$BEGET_API/dns/changeRecords" \
        --data-urlencode "login=$BEGET_Login" --data-urlencode "passwd=$BEGET_Password" \
        --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
        --data-urlencode "input_data=$new_records")

    if echo "$resp" | grep -q '"status":"success".*"status":"success"'; then
        _info "Beget: TXT added"
        return 0
    else
        _err "Beget: dns/changeRecords failed: $resp"
        return 1
    fi
}

dns_beget_rm() {
    fulldomain="$1"
    txtvalue="$2"
    BEGET_Login="${BEGET_Login:-$(_readaccountconf_mutable BEGET_Login)}"
    BEGET_Password="${BEGET_Password:-$(_readaccountconf_mutable BEGET_Password)}"

    _info "Beget: remove TXT $fulldomain = $txtvalue"

    cur_resp=$(curl -s -X POST "$BEGET_API/dns/getData" \
        --data-urlencode "login=$BEGET_Login" --data-urlencode "passwd=$BEGET_Password" \
        --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
        --data-urlencode "input_data={\"fqdn\":\"$fulldomain\"}")

    remaining=$(echo "$cur_resp" | $PYTHON_CMD -c "
import sys, json
try:
    d = json.load(sys.stdin)
    recs = d.get('answer', {}).get('result', {}).get('records', {}) or {}
    txts = recs.get('TXT', []) or []
    keep = [{'priority': 10, 'value': t.get('txtdata') or t.get('value')}
            for t in txts
            if (t.get('txtdata') or t.get('value')) != '$txtvalue']
    print(json.dumps({'fqdn': '$fulldomain', 'records': {'TXT': keep}}))
except Exception:
    print(json.dumps({'fqdn': '$fulldomain', 'records': {'TXT': []}}))
")
    curl -s -X POST "$BEGET_API/dns/changeRecords" \
        --data-urlencode "login=$BEGET_Login" --data-urlencode "passwd=$BEGET_Password" \
        --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
        --data-urlencode "input_data=$remaining" > /dev/null
    _info "Beget: TXT removed"
    return 0
}
