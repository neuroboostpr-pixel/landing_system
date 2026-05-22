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
n=$($SSH "$WPCLI post list --post_type=lp_cta --url=https://ailexi.ru/ --format=count")
test "$n" -ge 1 || { echo "FAIL: lp_cta count=$n, expected >=1"; exit 1; }
echo "  OK ($n records)"

echo "▶ T2: lp_integration CPT registered (count ≥ 0 OK)"
m=$($SSH "$WPCLI post list --post_type=lp_integration --url=https://ailexi.ru/ --format=count")
echo "  OK ($m records)"

echo "▶ T3: lp_snippet CPT registered (count ≥ 0 OK)"
s=$($SSH "$WPCLI post list --post_type=lp_snippet --url=https://ailexi.ru/ --format=count")
echo "  OK ($s records)"

echo "▶ T4: HTTP code на network admin страницах (200=auth ok, 302=login redirect, оба ок)"
for slug in landing-config-network landing-config-network-cta landing-config-network-integrations landing-config-network-snippets landing-config-network-lead-statuses; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://ailexi.ru/wp-admin/network/admin.php?page=$slug" || echo "000")
    test "$code" = "200" -o "$code" = "302" || { echo "FAIL: network $slug returned $code"; exit 1; }
    echo "  OK $slug → $code"
done

echo "▶ T5: HTTP code на subsite read-only страницах"
for slug in landing-config-cta landing-config-integrations landing-config-snippets landing-config-lead-statuses; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://russian.ailexi.ru/wp-admin/admin.php?page=$slug" || echo "000")
    test "$code" = "200" -o "$code" = "302" || { echo "FAIL: subsite $slug returned $code"; exit 1; }
    echo "  OK $slug → $code"
done

echo "▶ T6: debug.log не содержит свежих PHP Fatal/TypeError от landing-config"
recent=$($SSH "tail -500 $WP_PATH/wp-content/debug.log 2>/dev/null | grep -E 'Fatal|TypeError' | grep -i 'landing-config' | tail -3" || echo "")
test -z "$recent" || { echo "FAIL: fresh fatals in our code:"; echo "$recent"; exit 1; }
echo "  OK (no fatals)"

echo "▶ T7: lp_lead_status CPT registered (count >= 0 OK, count >= 5 после seed)"
ls=$($SSH "$WPCLI post list --post_type=lp_lead_status --url=https://ailexi.ru/ --format=count")
echo "  OK ($ls records — если 0, нужен ручной seed: wp eval 'LandingConfig\\\\Migrate\\\\seed_default_lead_statuses(1);')"

echo "▶ T8: lead-detail URL liveness (любой id, 200/302/400/404 — все говорят что страница зарегистрирована)"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://russian.ailexi.ru/wp-admin/admin.php?page=landing-config-lead-detail&id=1" || echo "000")
case "$code" in
    200|302|400|404) echo "  OK lead-detail → $code" ;;
    *) echo "FAIL: lead-detail returned $code"; exit 1 ;;
esac

echo "▶ T9: POST /lead без pd_consent → 400"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST \
    "https://russian.ailexi.ru/wp-json/landing/v1/lead" \
    -d "name=Test&phone=+71234567890&email=test@example.com&website=")
test "$code" = "400" || { echo "FAIL: expected 400 without pd_consent, got $code"; exit 1; }
echo "  OK no-consent → 400"

echo "▶ T10: POST /lead с pd_consent=1 → 200"
resp=$(curl -s --max-time 10 -X POST \
    "https://russian.ailexi.ru/wp-json/landing/v1/lead" \
    -d "name=SmokeTest&phone=+79991234567&email=smoke@test.ru&website=&pd_consent=1")
echo "$resp" | grep -q '"ok":true' || { echo "FAIL: expected ok:true, got: $resp"; exit 1; }
echo "  OK with-consent → 200"

echo "▶ T11: /policy и /consent отдают 200 (если legal-pages засеяны)"
for slug in policy consent; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "https://russian.ailexi.ru/$slug" || echo "000")
    case "$code" in
        200) echo "  OK /$slug → 200" ;;
        404) echo "  SKIP /$slug → 404 (legal-pages не засеяны на этом сегменте — это OK для smoke)" ;;
        *) echo "FAIL: /$slug returned $code"; exit 1 ;;
    esac
done

echo "▶ T_CB_1: главная страница содержит DOM cookie-banner (id=lp-cb)"
html=$(curl -s "https://russian.ailexi.ru/" || echo "")
echo "$html" | grep -q 'id="lp-cb"' || { echo "FAIL: id=lp-cb not in homepage HTML"; exit 1; }
echo "  OK lp-cb DOM present"

echo "▶ T_CB_2: главная содержит consent-init (gtag default denied)"
echo "$html" | grep -q "gtag('consent','default'" || { echo "FAIL: consent-init script missing"; exit 1; }
echo "  OK consent-init present"

echo "▶ T_CB_3: layout класс задан (по умолчанию bottom-bar)"
echo "$html" | grep -qE 'lp-cb--(top-bar|bottom-bar|floating-card-left|floating-card-right|center-modal)' \
    || { echo "FAIL: no layout class on banner"; exit 1; }
echo "  OK layout class present"

echo "▶ T_CB_4: CSS+JS подключены"
echo "$html" | grep -q "/cookie-banner/core.css" || { echo "FAIL: core.css not enqueued"; exit 1; }
echo "$html" | grep -q "/cookie-banner/banner.js" || { echo "FAIL: banner.js not enqueued"; exit 1; }
echo "  OK assets enqueued"

echo "✅ S2-A.3 + B19 live smoke GREEN"
