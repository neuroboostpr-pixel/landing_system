#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  DEPLOY="$REPO/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
  PLUGIN_SCRIPT="$REPO/skills/wp-cli-deployer/scripts/get-plugin-list.py"
}

@test "deploy script calls get-plugin-list.py" {
  run grep -q "get-plugin-list.py" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "plugin install block appears after theme activation" {
  activate_line=$(grep -n "Activate theme" "$DEPLOY" | head -n1 | cut -d: -f1)
  plugins_line=$(grep -n "Install plugins from design-stack" "$DEPLOY" | head -n1 | cut -d: -f1)
  [ -n "$activate_line" ]
  [ -n "$plugins_line" ]
  [ "$plugins_line" -gt "$activate_line" ]
}

@test "plugin install block appears before lazy-blocks" {
  plugins_line=$(grep -n "Install plugins from design-stack" "$DEPLOY" | head -n1 | cut -d: -f1)
  lazy_line=$(grep -n "Ensure lazy-blocks plugin" "$DEPLOY" | head -n1 | cut -d: -f1)
  [ "$plugins_line" -lt "$lazy_line" ]
}

@test "get-plugin-list.py script exists" {
  [ -f "$PLUGIN_SCRIPT" ]
}

@test "get-plugin-list.py includes litespeed-cache in defaults" {
  run python "$PLUGIN_SCRIPT" /nonexistent/design-stack.yaml
  [[ "$output" == *"litespeed-cache"* ]]
}

@test "get-plugin-list.py includes wordfence in defaults" {
  run python "$PLUGIN_SCRIPT" /nonexistent/design-stack.yaml
  [[ "$output" == *"wordfence"* ]]
}
