#!/usr/bin/env bash
# 03-sitemap-per-site.sh
# Each subsite must have its own /wp-sitemap.xml containing only its URLs.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="03-sitemap-per-site"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

for host in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
    url="http://$host/wp-sitemap.xml"
    info "GET $url"
    XML=$(curl -s -L --max-time 15 "$url" || echo "")

    if echo "$XML" | grep -q '<sitemapindex\|<urlset'; then
        pass "$url is valid XML sitemap"
    else
        fail "$url does NOT look like a sitemap (first 300 chars):"
        echo "$XML" | head -c 300; echo
        continue
    fi

    # Must reference this host, not the others
    if echo "$XML" | grep -q "$host"; then
        pass "$url references its own host"
    else
        fail "$url does not reference $host"
    fi

    # Should NOT reference OTHER subsites
    for other in ailexi.ru alpha.ailexi.ru bravo.ailexi.ru; do
        [ "$other" = "$host" ] && continue
        if echo "$XML" | grep -q "://$other/"; then
            fail "$url leaks references to $other (cross-site leak!)"
        fi
    done
done

finish_test
