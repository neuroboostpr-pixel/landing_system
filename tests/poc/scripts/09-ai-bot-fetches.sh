#!/usr/bin/env bash
# 09-ai-bot-fetches.sh
# Simulate AI crawlers (GPTBot, ClaudeBot, PerplexityBot) fetching the front page.
# Verify they receive server-rendered HTML with the block content (no JS required).

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/env.sh"
source "$HERE/../lib/assert.sh"

export CURRENT_TEST="09-ai-bot-fetches"
LOG="$LOGS_DIR/${CURRENT_TEST}.log"
exec > >(tee "$LOG") 2>&1
echo "=== $CURRENT_TEST started ==="

USER_AGENTS=(
    "GPTBot|Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
    "ClaudeBot|Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"
    "PerplexityBot|Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
)

HOSTS=(ailexi.ru alpha.ailexi.ru bravo.ailexi.ru)

for entry in "${USER_AGENTS[@]}"; do
    botname="${entry%%|*}"
    ua="${entry#*|}"
    info "Testing as $botname"
    for host in "${HOSTS[@]}"; do
        HTML=$(curl -s -L --max-time 20 -A "$ua" "http://$host/?_=$RANDOM" || echo "")
        # Content must be server-rendered: block class + headline visible to bots
        if echo "$HTML" | grep -q 'lazyblock-poc-hero'; then
            pass "[$botname] http://$host returns server-rendered block content"
        else
            fail "[$botname] http://$host did NOT return block content (size: ${#HTML} chars)"
        fi
        # FAQPage Schema.org (from 06) must also be visible
        if echo "$HTML" | grep -q '"@type":"FAQPage"'; then
            pass "[$botname] http://$host returns FAQPage Schema.org"
        else
            fail "[$botname] http://$host missing FAQPage Schema.org"
        fi
    done
done

finish_test
