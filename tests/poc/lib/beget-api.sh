#!/usr/bin/env bash
# Thin wrapper for Beget API: https://beget.com/ru/kb/api/
# All methods use input_format=json/output_format=json.

beget_api() {
  # beget_api <category/method> [extra_input_data_as_json]
  local method="$1"
  local input_data="${2:-{}}"
  curl -s -X POST "${BEGET_API}/${method}" \
    --data-urlencode "login=${BEGET_LOGIN}" \
    --data-urlencode "passwd=${BEGET_PASSWD}" \
    --data-urlencode "input_format=json" \
    --data-urlencode "output_format=json" \
    --data-urlencode "input_data=${input_data}"
}

# Check that response.status == success at both outer and inner levels.
beget_ok() {
  # beget_ok <json_response>
  local resp="$1"
  local outer inner
  outer=$(echo "$resp" | python -c 'import sys,json; d=json.load(sys.stdin); print(d.get("status",""))' 2>/dev/null)
  inner=$(echo "$resp" | python -c 'import sys,json; d=json.load(sys.stdin); print(d.get("answer",{}).get("status",""))' 2>/dev/null)
  [ "$outer" = "success" ] && [ "$inner" = "success" ]
}

# Pretty-print response result.
beget_result() {
  echo "$1" | python -c 'import sys,json; print(json.dumps(json.load(sys.stdin), indent=2, ensure_ascii=False))'
}

# Common operations we'll need:

beget_account_info() { beget_api "user/getAccountInfo"; }
beget_domain_list()  { beget_api "domain/getList"; }
beget_site_list()    { beget_api "site/getList"; }

beget_dns_get() {
  # beget_dns_get <fqdn>
  beget_api "dns/getData" "{\"fqdn\":\"$1\"}"
}

beget_dns_change() {
  # beget_dns_change <fqdn> <records_json>
  beget_api "dns/changeRecords" "{\"fqdn\":\"$1\",\"records\":$2}"
}

beget_subdomain_add() {
  # beget_subdomain_add <subdomain_name> <parent_fqdn>
  beget_api "domain/addSubdomain" "{\"subdomain\":\"$1\",\"domain\":\"$2\"}"
}

beget_mysql_add_db() {
  # beget_mysql_add_db <db_name> <db_password>
  beget_api "mysql/addDb" "{\"db_name\":\"$1\",\"access\":{\"localhost\":{\"password\":\"$2\"}}}"
}

beget_mysql_drop_db() {
  # beget_mysql_drop_db <db_name>
  beget_api "mysql/dropDb" "{\"db_name\":\"$1\"}"
}

beget_site_add() {
  # beget_site_add <site_name>
  beget_api "site/add" "{\"site_name\":\"$1\"}"
}

beget_domain_link_site() {
  # beget_domain_link_site <domain_id> <site_id>
  beget_api "domain/linkSite" "{\"domain_id\":\"$1\",\"site_id\":\"$2\"}"
}
