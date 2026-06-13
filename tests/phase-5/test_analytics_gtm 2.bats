#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  AGENT="$REPO/agents/analytics-engineer.md"
}

@test "analytics-engineer references GTM_CONTAINER_ID" {
  run grep -q "GTM_CONTAINER_ID" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "analytics-engineer contains lp_gtm_head function" {
  run grep -q "lp_gtm_head" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "analytics-engineer contains lp_gtm_body function" {
  run grep -q "lp_gtm_body" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "GTM noscript guarded by cookie consent check" {
  run grep -q "lp_cookie_consent" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "GTM head hook added with priority 2" {
  run grep -q "wp_head.*lp_gtm_head.*2" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "env.example contains GTM_CONTAINER_ID" {
  run grep -q "GTM_CONTAINER_ID" "$REPO/.env.example"
  [ "$status" -eq 0 ]
}
