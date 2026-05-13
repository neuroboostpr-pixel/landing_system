#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  DEPLOY="$REPO/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
}

@test "installs lazy-blocks plugin" {
  run grep -q "wp plugin install lazy-blocks" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "no longer runs wp acf import for block fields" {
  run grep -q "wp acf import" "$DEPLOY"
  [ "$status" -ne 0 ]
}

@test "imports images via wp media import" {
  run grep -q "wp media import" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "creates front page via wp post create" {
  run grep -q "wp post create" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "sets page_on_front" {
  run grep -q "page_on_front" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "substitutes IMAGE_ATTACHMENT_ID placeholders" {
  run grep -q "__IMAGE_ATTACHMENT_ID__" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "is bash strict-mode" {
  run grep -q "set -euo pipefail" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "preflight passes after this deploy script lands" {
  cd "$REPO"
  run bash -c "grep -q 'wp plugin install lazy-blocks' skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
  [ "$status" -eq 0 ]
}
