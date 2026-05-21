#!/usr/bin/env bash
# 10-clone-subsite.sh
# Create a NEW subsite (clone.ailexi.ru) and copy front-page content from alpha
# to verify the "clone" workflow works end-to-end.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/beget-api.sh"
source "$HERE/../lib/ssh.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="10-clone-subsite"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

CLONE_HOST="clone.ailexi.ru"
DOMAIN_ID=12513532

info "Step 1: ensure $CLONE_HOST subdomain exists in Beget DNS"
EXISTS=$(curl -s -X POST "$BEGET_API/domain/getSubdomainList" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  | python -c "import sys,json; d=json.load(sys.stdin); has=any(x['fqdn']=='$CLONE_HOST' for x in d['answer']['result']); print('yes' if has else 'no')")

if [ "$EXISTS" = "no" ]; then
    curl -s -X POST "$BEGET_API/domain/addSubdomainVirtual" \
      --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
      --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
      --data-urlencode "input_data={\"subdomain\":\"clone\",\"domain_id\":${DOMAIN_ID}}" > /dev/null
    info "Beget subdomain $CLONE_HOST created"
    sleep 5
fi
pass "Beget subdomain ready"

info "Step 2: link to site (so nginx routes it) and set PHP 8.3"
SITE_ID=9192816
# Get the subdomain id we just created
CLONE_ID=$(curl -s -X POST "$BEGET_API/domain/getSubdomainList" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(x['id']) for x in d['answer']['result'] if x['fqdn']=='$CLONE_HOST']" | head -1)

curl -s -X POST "$BEGET_API/site/linkDomain" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  --data-urlencode "input_data={\"domain_id\":$CLONE_ID,\"site_id\":$SITE_ID}" > /dev/null

curl -s -X POST "$BEGET_API/domain/changePhpVersion" \
  --data-urlencode "login=$BEGET_LOGIN" --data-urlencode "passwd=$BEGET_PASSWD" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  --data-urlencode "input_data={\"full_fqdn\":\"$CLONE_HOST\",\"php_version\":\"8.3\"}" > /dev/null
info "linked + PHP 8.3 set"
sleep 60

info "Step 3: wp site create + export page from alpha + import into clone"

# Idempotent: delete existing clone WP-site if any
ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP site delete --slug=clone --yes 2>&1 | tail -1 || true"

# Create new WP subsite
RES=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP site create --slug=clone --title='Clone of Alpha' --porcelain 2>&1" | tail -1)
if echo "$RES" | grep -qE '^[0-9]+$'; then
    pass "wp site create clone returned blog_id=$RES"
else
    fail "wp site create failed: $RES"
    finish_test
fi

# Export content of alpha's front page
ALPHA_PAGE_ID=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://alpha.ailexi.ru option get page_on_front 2>&1" | tail -1)
EXPORT=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://alpha.ailexi.ru post get $ALPHA_PAGE_ID --field=content 2>&1")

# Create same page on clone
CLONE_PAGE_ID=$(ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$CLONE_HOST post create --post_type=page --post_status=publish --post_title='Cloned page' --post_content='$EXPORT' --porcelain 2>&1" | tail -1)
if echo "$CLONE_PAGE_ID" | grep -qE '^[0-9]+$'; then
    pass "cloned page created (id=$CLONE_PAGE_ID)"
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$CLONE_HOST option update show_on_front page 2>&1" > /dev/null
    ssh_run "cd ~/${TEST_DOMAIN}/public_html && $REMOTE_WP --url=http://$CLONE_HOST option update page_on_front $CLONE_PAGE_ID 2>&1" > /dev/null
else
    fail "clone page create failed: $CLONE_PAGE_ID"
fi

info "Step 4: verify cloned subsite renders the block"
sleep 5
HTML=$(curl -s -L --max-time 20 "http://$CLONE_HOST/?_=$RANDOM" || echo "")
if echo "$HTML" | grep -q 'lazyblock-poc-hero'; then
    pass "GET http://$CLONE_HOST/ renders cloned block"
else
    fail "GET http://$CLONE_HOST/ does NOT render block (size: ${#HTML})"
    echo "$HTML" | head -c 600; echo
fi

finish_test
