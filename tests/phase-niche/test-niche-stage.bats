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

@test "stage-gates has 01a_niche_analysis block" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q '"01a_niche_analysis":' "$GATES"
}

@test "stage-gates 02_assets requires 01a_niche_analysis approved" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  # Convert POSIX path to Windows path for Python on Windows
  WIN_GATES="$(cygpath -w "$GATES" 2>/dev/null || echo "$GATES" | sed 's|^/\([a-z]\)/|\1:/|')"
  python -c "import yaml,sys; d=yaml.safe_load(open(r'$WIN_GATES',encoding='utf-8')); sys.exit(0 if '01a_niche_analysis' in d['stages']['02_assets'].get('require_approved',[]) else 1)"
}

@test "stage-gates 01a hard checks include three artifacts" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "niche-analysis.md" "$GATES"
  grep -q "competitors.yaml" "$GATES"
  grep -q "positioning.md" "$GATES"
}

@test "niche-analyst agent file exists" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  [ -f "$AGENT" ]
}

@test "niche-analyst has frontmatter with name and description" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "^name: niche-analyst" "$AGENT"
  grep -q "^description:" "$AGENT"
}

@test "niche-analyst mentions all 7 roles" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  for role in direct local_dealer manufacturer analog category_leader local_competitor indirect; do
    grep -q "$role" "$AGENT" || { echo "missing role: $role"; return 1; }
  done
}

@test "niche-analyst documents zero-touch principle" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -qi "zero-touch\|никаких вопросов\|без вопросов" "$AGENT"
}
