#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  AGENT="$REPO/agents/migration-engineer.md"
  SCRIPT="$REPO/skills/wp-cli-deployer/scripts/import-redirects.py"
}

@test "migration-engineer agent file exists" {
  [ -f "$AGENT" ]
}

@test "agent references import-redirects.py" {
  run grep -q "import-redirects.py" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "agent references redirects.csv" {
  run grep -q "redirects.csv" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "agent has wiki log pre-flight" {
  run grep -q "wiki.log.*migration-engineer" "$AGENT"
  [ "$status" -eq 0 ]
}

@test "import-redirects.py validates external source rejects" {
  run python "$SCRIPT" /nonexistent.csv
  [ "$status" -ne 0 ]
}

@test "import-redirects.py validate-only flag accepted" {
  TMPFILE=$(mktemp /tmp/redirects.XXXXXX.csv)
  echo "source,target,code" > "$TMPFILE"
  echo "/old,/new,301" >> "$TMPFILE"
  run python "$SCRIPT" "$TMPFILE" --validate-only
  rm -f "$TMPFILE"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OK"* ]]
}
