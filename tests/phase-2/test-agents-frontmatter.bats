#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "client-assets-collector agent file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.agents/client-assets-collector.md"
}

@test "client-assets-collector has valid frontmatter" {
  run grep -E "^name: client-assets-collector$" "$LANDING_SYSTEM_ROOT/.agents/client-assets-collector.md"
  [ "$status" -eq 0 ]
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.agents/client-assets-collector.md"
  [ "$status" -eq 0 ]
}

@test "photo-stylist agent file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.agents/photo-stylist.md"
}

@test "photo-stylist has valid frontmatter" {
  run grep -E "^name: photo-stylist$" "$LANDING_SYSTEM_ROOT/.agents/photo-stylist.md"
  [ "$status" -eq 0 ]
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.agents/photo-stylist.md"
  [ "$status" -eq 0 ]
}
