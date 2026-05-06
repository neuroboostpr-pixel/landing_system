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
