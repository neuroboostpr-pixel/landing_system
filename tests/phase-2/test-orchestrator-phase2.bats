#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "landing-orchestrator has Phase 2 Scope section" {
  run grep -c "Phase 2 Scope" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-orchestrator mentions client-assets-collector" {
  run grep -c "client-assets-collector" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-orchestrator mentions photo-stylist" {
  run grep -c "photo-stylist" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-orchestrator mentions references-curator" {
  run grep -c "references-curator" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-orchestrator mentions moodboard-composer" {
  run grep -c "moodboard-composer" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-orchestrator mentions style-extractor" {
  run grep -c "style-extractor" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "landing-orchestrator mentions brand-architect" {
  run grep -c "brand-architect" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}
