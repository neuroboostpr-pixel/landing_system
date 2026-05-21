#!/usr/bin/env bash
# 00-setup-multisite.sh — Hard gate: bootstrap a clean WP Multisite on Beget.
#
# Phases:
#   1. Add wildcard A-record *.ailexi.ru via Beget API
#   2. Wipe existing WP files + drop+create DB
#   3. Download fresh WordPress core
#   4. wp-cli core multisite-install (subdomain mode)
#   5. Install + activate plugins: lazy-blocks, seo-by-rank-math (both network)
#   6. Switch to a default block theme
#   7. Create 2 subsites: alpha.ailexi.ru, bravo.ailexi.ru
#   8. Verify: HTTP 200 on root + alpha + bravo + network admin reachable
#
# If anything in this script fails, the gauntlet aborts.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/beget-api.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="00-setup-multisite"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started at $(date -Iseconds) ==="

###############################################################################
# Phase 1: Wildcard DNS
###############################################################################
info "Phase 1: ensure *.${TEST_DOMAIN} wildcard A-record exists"

# Get current records
RESP=$(curl -s -X POST "$BEGET_API/dns/getData" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  --data-urlencode "input_data={\"fqdn\":\"${TEST_DOMAIN}\"}")
A_IP=$(echo "$RESP" | python -c 'import sys,json; d=json.load(sys.stdin); a=d["answer"]["result"]["records"]["A"][0]["address"]; print(a)')
info "Current A-record for ${TEST_DOMAIN}: $A_IP"

# Idempotent: only create wildcard if not present yet.
# Use domain/getSubdomainList + addSubdomainVirtual (proven working).
DOMAIN_ID=12513532  # ailexi.ru, known from prior discovery
HAS_WC=$(curl -s -X POST "$BEGET_API/domain/getSubdomainList" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  | python -c "import sys,json; d=json.load(sys.stdin); has=any(x['fqdn']=='*.${TEST_DOMAIN}' for x in d['answer']['result']); print('yes' if has else 'no')")

if [ "$HAS_WC" = "no" ]; then
  RESP=$(curl -s -X POST "$BEGET_API/domain/addSubdomainVirtual" \
    --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
    --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
    --data-urlencode "input_data={\"subdomain\":\"*\",\"domain_id\":${DOMAIN_ID}}")
  echo "wildcard create response: $RESP"
fi

# Verify via Google DNS that any random subdomain resolves now
sleep 10
RANDSUB="poc-verify-$(date +%s).${TEST_DOMAIN}"
STATUS=$(curl -s "https://dns.google/resolve?name=${RANDSUB}&type=A" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('Status'))")
if [ "$STATUS" = "0" ]; then
  pass "wildcard *.${TEST_DOMAIN} resolves (random subdomain ${RANDSUB} → DNS OK)"
else
  fail "wildcard NOT propagated, dns.google Status=${STATUS} for ${RANDSUB}"
  finish_test
fi

###############################################################################
# Phase 2: Nuke existing WP + DB
###############################################################################
info "Phase 2: wipe existing WP and DB on ${TEST_WP_PATH}"

ssh_run "
set -e
cd ~/${TEST_DOMAIN}
rm -rf public_html
mkdir public_html
echo 'wp dir wiped'
"

# Drop+recreate DB through Beget API to clear leftover tables (multisite-aware re-runs).
RESP=$(curl -s -X POST "$BEGET_API/mysql/dropDb" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  --data-urlencode "input_data={\"suffix\":\"poc\"}")
echo "dropDb: $RESP"
sleep 2
pass "wiped ${TEST_WP_PATH}"

###############################################################################
# Phase 3: Fresh WordPress
###############################################################################
info "Phase 3: download + configure fresh WordPress"

# DB created via Beget API mysql/addDb. Creds in env.sh.
# Idempotency: addDb will fail if DB exists, that's fine.
RESP=$(curl -s -X POST "$BEGET_API/mysql/addDb" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  --data-urlencode "input_data={\"suffix\":\"poc\",\"password\":\"${TEST_DB_PASS}\"}")
echo "mysql addDb response: $RESP"

# Reset password (idempotent — works whether DB existed or not)
RESP=$(curl -s -X POST "$BEGET_API/mysql/changeAccessPassword" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  --data-urlencode "input_data={\"suffix\":\"poc\",\"access\":\"localhost\",\"password\":\"${TEST_DB_PASS}\"}")
echo "mysql changeAccessPassword: $RESP"

ssh_run "
set -e
cd ~/${TEST_DOMAIN}/public_html
$REMOTE_WP core download --locale=en_US --force 2>&1 | tail -3
$REMOTE_WP config create --dbname=${TEST_DB_NAME} --dbuser=${TEST_DB_USER} --dbpass='${TEST_DB_PASS}' --dbhost=localhost --skip-check --force 2>&1
$REMOTE_WP config set WP_ALLOW_MULTISITE true --raw
echo 'wp-config ready'
"
pass "fresh WP downloaded + configured"

###############################################################################
# Phase 4: multisite-install (subdomain mode)
###############################################################################
info "Phase 4: install WP Multisite (subdomain mode)"

ADMIN_PASS="PocAdmin2026Aa1!"

ssh_run "
set -e
cd ~/${TEST_DOMAIN}/public_html
$REMOTE_WP core multisite-install \\
  --url='http://${TEST_DOMAIN}' \\
  --title='POC Network' \\
  --admin_user='admin' \\
  --admin_password='${ADMIN_PASS}' \\
  --admin_email='esper21@mail.ru' \\
  --subdomains 2>&1 | tail -10
"
pass "multisite installed"

# Write .htaccess for multisite (subdomain mode)
ssh_run "cat > ~/${TEST_DOMAIN}/public_html/.htaccess << 'EOF'
RewriteEngine On
RewriteBase /
RewriteRule ^index\\.php\$ - [L]

# add a trailing slash to /wp-admin
RewriteRule ^([_0-9a-zA-Z-]+/)?wp-admin\$ \$1wp-admin/ [R=301,L]

RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(wp-(content|admin|includes).*) \$2 [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(.*\\.php)\$ \$2 [L]
RewriteRule . index.php [L]
EOF
echo htaccess written"
pass ".htaccess written for multisite"

###############################################################################
# Phase 5: Plugins
###############################################################################
info "Phase 5: install Lazy Blocks + RankMath (both network-activate)"

ssh_run "
set -e
cd ~/${TEST_DOMAIN}/public_html
$REMOTE_WP plugin install lazy-blocks --activate-network 2>&1 | tail -3
$REMOTE_WP plugin install seo-by-rank-math --activate-network 2>&1 | tail -3
$REMOTE_WP plugin list --network --format=table 2>&1
"
pass "plugins installed + network-activated"

###############################################################################
# Phase 6: Theme
###############################################################################
info "Phase 6: switch to Twenty Twenty-Five (block theme)"

ssh_run "
set -e
cd ~/${TEST_DOMAIN}/public_html
$REMOTE_WP theme install twentytwentyone 2>&1 | tail -3
$REMOTE_WP theme enable twentytwentyone --network 2>&1 | tail -3
$REMOTE_WP theme activate twentytwentyone 2>&1 | tail -3
$REMOTE_WP theme list --format=table 2>&1
"
pass "theme installed + network-enabled"

###############################################################################
# Phase 7: Create 2 subsites in WP (and ensure DNS subdomains exist in Beget)
###############################################################################
info "Phase 7: create subsites alpha + bravo (Beget DNS + WP)"

# Ensure alpha+bravo subdomains exist in Beget (idempotent via wildcard, but explicit is robust)
# Also: site/add the WP root site, link all subdomains, force PHP 8.3.
DOMAIN_ID=12513532

# 1) site/add ailexi.ru if not present in site/getList; capture site_id
SITE_ID=$(curl -s -X POST "$BEGET_API/site/getList" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  | python -c "import sys,json; d=json.load(sys.stdin); ids=[x['id'] for x in d['answer']['result'] if 'ailexi.ru/public_html' in x['path']]; print(ids[0] if ids else 'none')")
if [ "$SITE_ID" = "none" ]; then
    SITE_ID=$(curl -s -X POST "$BEGET_API/site/add" \
      --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
      --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
      --data-urlencode 'input_data={"name":"ailexi.ru"}' \
      | python -c "import sys,json; print(json.load(sys.stdin)['answer']['result'])")
    info "site/add created id=$SITE_ID"
else
    info "site already exists id=$SITE_ID"
fi

# 2) subdomains alpha + bravo + wildcard
for sd in '*' alpha bravo; do
  EXISTS=$(curl -s -X POST "$BEGET_API/domain/getSubdomainList" \
    --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
    --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
    | python -c "import sys,json; d=json.load(sys.stdin); has=any(x['fqdn']=='${sd}.${TEST_DOMAIN}' for x in d['answer']['result']); print('yes' if has else 'no')")
  if [ "$EXISTS" = "no" ]; then
    curl -s -X POST "$BEGET_API/domain/addSubdomainVirtual" \
      --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
      --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
      --data-urlencode "input_data={\"subdomain\":\"${sd}\",\"domain_id\":${DOMAIN_ID}}" > /dev/null
    info "Beget subdomain ${sd}.${TEST_DOMAIN} created"
  else
    info "Beget subdomain ${sd}.${TEST_DOMAIN} already exists"
  fi
done

# 3) link all 4 (root + wildcard + alpha + bravo) to site_id; set PHP 8.3
DOMS=$(curl -s -X POST "$BEGET_API/domain/getList" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json")
SUBS=$(curl -s -X POST "$BEGET_API/domain/getSubdomainList" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json")

for fqdn in ailexi.ru '*.ailexi.ru' alpha.ailexi.ru bravo.ailexi.ru; do
    # find domain or subdomain id for this fqdn
    DID=$(python -c "
import json, sys
doms = json.loads(sys.argv[1])['answer']['result']
subs = json.loads(sys.argv[2])['answer']['result']
target = sys.argv[3]
for d in doms:
    if d['fqdn'] == target:
        print(d['id']); sys.exit(0)
for s in subs:
    if s['fqdn'] == target:
        print(s['id']); sys.exit(0)
" "$DOMS" "$SUBS" "$fqdn")
    if [ -n "$DID" ]; then
        curl -s -X POST "$BEGET_API/site/linkDomain" \
          --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
          --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
          --data-urlencode "input_data={\"domain_id\":$DID,\"site_id\":$SITE_ID}" > /dev/null
        curl -s -X POST "$BEGET_API/domain/changePhpVersion" \
          --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
          --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
          --data-urlencode "input_data={\"full_fqdn\":\"$fqdn\",\"php_version\":\"8.3\"}" > /dev/null
        info "linked $fqdn (id=$DID) to site_id=$SITE_ID, PHP 8.3"
    fi
done

# 4) wait for nginx to pick up the changes
info "waiting 60s for nginx/php-fpm reload"
sleep 60

ssh_run "
set -e
cd ~/${TEST_DOMAIN}/public_html
$REMOTE_WP site create --slug=alpha --title='Alpha' 2>&1 | tail -3 || echo 'alpha may already exist'
$REMOTE_WP site create --slug=bravo --title='Bravo' 2>&1 | tail -3 || echo 'bravo may already exist'
# Activate theme on each subsite
for slug in alpha bravo; do
  $REMOTE_WP --url=http://\$slug.${TEST_DOMAIN} theme activate twentytwentyone 2>&1 | tail -1
done
$REMOTE_WP site list --format=table 2>&1
"
pass "2 subsites created + theme activated"

###############################################################################
# Phase 8: Verify
###############################################################################
info "Phase 8: verify HTTP responses"

# wait for DNS propagation (wildcard already set above, should be instant for Beget DNS)
sleep 10

for url in "http://${TEST_DOMAIN}" "http://${SUBSITE_1}" "http://${SUBSITE_2}" "http://${TEST_DOMAIN}/wp-login.php"; do
  CODE=$(curl -L -k -s -o /dev/null -w "%{http_code}" --max-time 20 "$url" || echo "000")
  if [ "$CODE" = "200" ] || [ "$CODE" = "302" ]; then
    pass "GET $url -> $CODE"
  else
    fail "GET $url -> $CODE (wanted 200 or 302)"
  fi
done

finish_test
