#!/usr/bin/env bats
# tests/phase-5/test-agents-phase5.bats
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
AGENTS_DIR="$REPO_ROOT/agents"

@test "system-setup.md exists" { [ -f "$AGENTS_DIR/system-setup.md" ]; }
@test "system-setup.md has name frontmatter" { grep -q "^name: system-setup" "$AGENTS_DIR/system-setup.md"; }

@test "wp-deployer.md exists" { [ -f "$AGENTS_DIR/wp-deployer.md" ]; }
@test "wp-deployer.md has name frontmatter" { grep -q "^name: wp-deployer" "$AGENTS_DIR/wp-deployer.md"; }
@test "wp-deployer.md has HARD GATE" { grep -qi "hard gate" "$AGENTS_DIR/wp-deployer.md"; }
@test "wp-deployer.md mentions rsync" { grep -q "rsync" "$AGENTS_DIR/wp-deployer.md"; }

@test "qa-auditor.md exists" { [ -f "$AGENTS_DIR/qa-auditor.md" ]; }
@test "qa-auditor.md has name frontmatter" { grep -q "^name: qa-auditor" "$AGENTS_DIR/qa-auditor.md"; }
@test "qa-auditor.md has HARD GATE" { grep -qi "hard gate" "$AGENTS_DIR/qa-auditor.md"; }

@test "lifecycle-keeper.md exists" { [ -f "$AGENTS_DIR/lifecycle-keeper.md" ]; }
@test "lifecycle-keeper.md has name frontmatter" { grep -q "^name: lifecycle-keeper" "$AGENTS_DIR/lifecycle-keeper.md"; }
