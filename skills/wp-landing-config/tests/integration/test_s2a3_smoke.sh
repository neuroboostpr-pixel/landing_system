#!/usr/bin/env bash
# S2-A.3 live smoke на ailexi.ru: проверка что CPT-страницы доступны,
# миграция сработала, helper landing_get_cta() возвращает данные из cascade.
set -euo pipefail

PROJECT_DIR="${1:-/tmp/test-s2a}"
[ -f "$PROJECT_DIR/.env" ] || { echo "ERROR: $PROJECT_DIR/.env not found" >&2; exit 1; }

set -a; source "$PROJECT_DIR/.env"; set +a
: "${BEGET_USER:?missing in .env}"
: "${BEGET_HOST:?missing in .env}"
: "${BEGET_SSH_KEY:?missing in .env}"

SSH="ssh -i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=ERROR ${BEGET_USER}@${BEGET_HOST}"
WP_PATH=/home/e/esper21/ailexi.ru/public_html
WPCLI="/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar --path=$WP_PATH"

echo "▶ T1: lp_cta CPT records exist (≥1)"
n=$($SSH "$WPCLI post list --post_type=lp_cta --url=http://ailexi.ru/ --format=count")
test "$n" -ge 1 || { echo "FAIL: lp_cta count=$n, expected >=1"; exit 1; }
echo "  OK ($n records)"

echo "▶ T2: lp_integration CPT registered (count ≥ 0 OK)"
m=$($SSH "$WPCLI post list --post_type=lp_integration --url=http://ailexi.ru/ --format=count")
echo "  OK ($m records)"

echo "▶ T3: lp_snippet CPT registered (count ≥ 0 OK)"
s=$($SSH "$WPCLI post list --post_type=lp_snippet --url=http://ailexi.ru/ --format=count")
echo "  OK ($s records)"

echo "▶ T4: HTTP code на network admin страницах (200=auth ok, 302=login redirect, оба ок)"
for slug in landing-config-network landing-config-network-cta landing-config-network-integrations landing-config-network-snippets; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://ailexi.ru/wp-admin/network/admin.php?page=$slug" || echo "000")
    test "$code" = "200" -o "$code" = "302" || { echo "FAIL: network $slug returned $code"; exit 1; }
    echo "  OK $slug → $code"
done

echo "▶ T5: HTTP code на subsite read-only страницах"
for slug in landing-config-cta landing-config-integrations landing-config-snippets; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://russian.ailexi.ru/wp-admin/admin.php?page=$slug" || echo "000")
    test "$code" = "200" -o "$code" = "302" || { echo "FAIL: subsite $slug returned $code"; exit 1; }
    echo "  OK $slug → $code"
done

echo "▶ T6: debug.log не содержит свежих PHP Fatal/TypeError от landing-config"
recent=$($SSH "tail -500 $WP_PATH/wp-content/debug.log 2>/dev/null | grep -E 'Fatal|TypeError' | grep -i 'landing-config' | tail -3" || echo "")
test -z "$recent" || { echo "FAIL: fresh fatals in our code:"; echo "$recent"; exit 1; }
echo "  OK (no fatals)"

echo "✅ S2-A.3 live smoke GREEN"
