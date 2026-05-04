#!/usr/bin/env bats
# tests/phase-5/test-commands-phase5.bats
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
COMMANDS_DIR="$REPO_ROOT/.claude/commands"
SKILLS_DIR="$REPO_ROOT/skills"
SCRIPTS_DIR="$REPO_ROOT/scripts"

@test "landing-setup.md exists" { [ -f "$COMMANDS_DIR/landing-setup.md" ]; }
@test "landing-setup.md has description" { grep -q "^description:" "$COMMANDS_DIR/landing-setup.md"; }

@test "landing-deploy.md exists" { [ -f "$COMMANDS_DIR/landing-deploy.md" ]; }
@test "landing-deploy.md mentions rsync" { grep -q "rsync" "$COMMANDS_DIR/landing-deploy.md"; }

@test "landing-qa.md exists" { [ -f "$COMMANDS_DIR/landing-qa.md" ]; }
@test "landing-qa.md has description" { grep -q "^description:" "$COMMANDS_DIR/landing-qa.md"; }

@test "landing-rollback.md exists" { [ -f "$COMMANDS_DIR/landing-rollback.md" ]; }
@test "landing-clone.md exists" { [ -f "$COMMANDS_DIR/landing-clone.md" ]; }

@test "preflight.sh exists and executable" {
  [ -f "$SCRIPTS_DIR/preflight.sh" ]
  [ -x "$SCRIPTS_DIR/preflight.sh" ]
}

@test "deploy.sh exists and executable" {
  [ -f "$SCRIPTS_DIR/deploy.sh" ]
  [ -x "$SCRIPTS_DIR/deploy.sh" ]
}

@test "wp-cli-deployer SKILL.md exists" { [ -f "$SKILLS_DIR/wp-cli-deployer/SKILL.md" ]; }
@test "deploy-wordpress.sh exists and executable" {
  [ -f "$SKILLS_DIR/wp-cli-deployer/scripts/deploy-wordpress.sh" ]
  [ -x "$SKILLS_DIR/wp-cli-deployer/scripts/deploy-wordpress.sh" ]
}

@test "landing-versioning SKILL.md exists" { [ -f "$SKILLS_DIR/landing-versioning-and-cloning/SKILL.md" ]; }
@test "create-version.sh exists and executable" {
  [ -f "$SKILLS_DIR/landing-versioning-and-cloning/scripts/create-version.sh" ]
  [ -x "$SKILLS_DIR/landing-versioning-and-cloning/scripts/create-version.sh" ]
}
@test "clone-landing.sh exists and executable" {
  [ -f "$SKILLS_DIR/landing-versioning-and-cloning/scripts/clone-landing.sh" ]
  [ -x "$SKILLS_DIR/landing-versioning-and-cloning/scripts/clone-landing.sh" ]
}

@test "generate-popup.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-popup.py" ]
}
@test "generate-js-init.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-js-init.py" ]
}
@test "generate-analytics.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-analytics.py" ]
}
@test "generate-integrations.py exists" {
  [ -f "$SKILLS_DIR/wp-gutenberg-block-builder/scripts/generate-integrations.py" ]
}
@test "config/system.yaml.template exists" { [ -f "$REPO_ROOT/config/system.yaml.template" ]; }
