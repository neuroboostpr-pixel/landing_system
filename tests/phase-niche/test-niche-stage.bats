#!/usr/bin/env bats

setup() {
  TEMPLATE_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template" && pwd)"
}

@test "template has 01a_АНАЛИЗ_НИШИ folder" {
  [ -d "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ" ]
}

@test "template 01a folder has README" {
  [ -f "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md" ]
}

@test "template 01a README mentions three artifacts" {
  grep -q "niche-analysis.md" "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md"
  grep -q "competitors.yaml" "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md"
  grep -q "positioning.md" "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md"
}

@test "landing-state template has 01a_niche_analysis stage" {
  grep -q '"01a_niche_analysis"' "$TEMPLATE_DIR/.landing-state.yaml"
}

@test "landing-state 01a is locked initially" {
  grep -E '"01a_niche_analysis":\s+\{status: locked' "$TEMPLATE_DIR/.landing-state.yaml"
}
