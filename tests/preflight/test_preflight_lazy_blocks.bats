#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
}

@test "preflight delegates to validate-all.sh" {
  run grep -q "validate-all.sh" "$REPO/scripts/preflight.sh"
  [ "$status" -eq 0 ]
}

@test "validate-all.sh checks deploy script for lazy-blocks install" {
  run grep -qE 'lazy-blocks' "$REPO/scripts/validate-all.sh"
  [ "$status" -eq 0 ]
}

@test "validate-all.sh fails fast when deploy script lacks lazy-blocks install" {
  # Spin a temp copy of validate-all.sh with a sabotaged deploy script.
  tmpdir="$(mktemp -d)"
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/scripts" "$tmpdir/skills/wp-cli-deployer/scripts"
  cp "$REPO/scripts/validate-all.sh" "$tmpdir/scripts/validate-all.sh"
  echo '#!/bin/bash' > "$tmpdir/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
  echo 'echo "no lazy-blocks here"' >> "$tmpdir/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
  cd "$tmpdir"
  run bash scripts/validate-all.sh
  [ "$status" -ne 0 ]
  echo "$output" | grep -q "lazy-blocks"
}
