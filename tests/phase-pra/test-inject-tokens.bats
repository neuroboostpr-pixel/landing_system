#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  INJECTOR="$ROOT/skills/block-composition/scripts/inject-tokens.py"
}

@test "replaces --color-accent in template" {
  cat > "$BATS_TMPDIR/in.html" <<EOF
<html><head><style>
:root { --color-bg: #fff; --color-fg: #000; --color-accent: #333; }
</style></head><body></body></html>
EOF
  run python3 "$INJECTOR" "$BATS_TMPDIR/in.html" "$FIXTURES/tokens-sample.json" "$BATS_TMPDIR/out.html"
  [ "$status" -eq 0 ]
  grep -q -- "--color-accent: #ff4d4d" "$BATS_TMPDIR/out.html"
}

@test "replaces --font-display in template" {
  cat > "$BATS_TMPDIR/in2.html" <<EOF
<html><head><style>
:root { --font-display: system-ui, sans-serif; --font-body: serif; }
</style></head><body></body></html>
EOF
  python3 "$INJECTOR" "$BATS_TMPDIR/in2.html" "$FIXTURES/tokens-sample.json" "$BATS_TMPDIR/out2.html"
  grep -q -- "--font-display: Manrope, sans-serif" "$BATS_TMPDIR/out2.html"
}

@test "preserves CSS vars not present in tokens.json" {
  cat > "$BATS_TMPDIR/in3.html" <<EOF
<html><head><style>
:root { --color-unknown: pink; --color-accent: #333; }
</style></head><body></body></html>
EOF
  python3 "$INJECTOR" "$BATS_TMPDIR/in3.html" "$FIXTURES/tokens-sample.json" "$BATS_TMPDIR/out3.html"
  grep -q -- "--color-unknown: pink" "$BATS_TMPDIR/out3.html"
  grep -q -- "--color-accent: #ff4d4d" "$BATS_TMPDIR/out3.html"
}
