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

# Prototype-first (e2d5a2c): стадии 00/01/01a/02 = n/a, поэтому 02_assets
# больше НЕ требует approved 01a — gate стал soft-lock без зависимостей.
@test "stage-gates 02_assets is soft-lock without 01a dependency (prototype-first)" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  # Convert POSIX path to Windows path for Python on Windows
  WIN_GATES="$(cygpath -w "$GATES" 2>/dev/null || echo "$GATES" | sed 's|^/\([a-z]\)/|\1:/|')"
  python3 -c "import yaml,sys; s=yaml.safe_load(open(r'$WIN_GATES',encoding='utf-8'))['stages']['02_assets']; sys.exit(0 if s.get('lock')=='soft' and '01a_niche_analysis' not in s.get('require_approved',[]) else 1)"
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

@test "landing-niche command exists in commands/" {
  CMD="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../commands" && pwd)/landing-niche.md"
  [ -f "$CMD" ]
}

@test "landing-niche command exists in .claude/commands/" {
  CMD="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.claude/commands" && pwd)/landing-niche.md"
  [ -f "$CMD" ]
}

@test "landing-niche command files are identical" {
  A="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../commands" && pwd)/landing-niche.md"
  B="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.claude/commands" && pwd)/landing-niche.md"
  diff -q "$A" "$B"
}

@test "landing-niche invokes niche-analyst agent" {
  CMD="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../commands" && pwd)/landing-niche.md"
  grep -q "niche-analyst" "$CMD"
}

@test "niche-analysis SKILL.md exists" {
  SKILL="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../skills" && pwd)/niche-analysis/SKILL.md"
  [ -f "$SKILL" ]
}

@test "niche-analysis SKILL has frontmatter" {
  SKILL="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../skills" && pwd)/niche-analysis/SKILL.md"
  grep -q "^name:" "$SKILL"
  grep -q "^description:" "$SKILL"
}

@test "orchestrator knows about 01a_niche_analysis" {
  ORC="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/landing-orchestrator.md"
  grep -q "01a_niche_analysis\|01a_АНАЛИЗ_НИШИ" "$ORC"
}

@test "orchestrator references niche-analyst" {
  ORC="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/landing-orchestrator.md"
  grep -q "niche-analyst" "$ORC"
}

@test "references-curator reads competitors.yaml" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/references-curator.md"
  grep -q "competitors.yaml\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "moodboard-composer reads niche-analysis.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/moodboard-composer.md"
  grep -q "niche-analysis.md\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "brand-architect reads positioning.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/brand-architect.md"
  grep -q "positioning.md\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "content-writer reads positioning.md and competitors.yaml" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/content-writer.md"
  grep -q "positioning.md" "$AGENT"
  grep -q "competitors.yaml" "$AGENT"
}

@test "seo-optimizer reads competitors.yaml" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/seo-optimizer.md"
  grep -q "competitors.yaml\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "root README mentions /landing-niche command" {
  README="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)/README.md"
  grep -q "/landing-niche" "$README"
}

@test "template CLAUDE.md mentions stage 01a" {
  CL="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template" && pwd)/CLAUDE.md"
  grep -q "01a_АНАЛИЗ_НИШИ\|01a" "$CL"
}

@test "package.json has test:phase-niche script" {
  PKG="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)/package.json"
  grep -q "test:phase-niche" "$PKG"
}

@test "niche-analyst documents step 9 visual requirements" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "visual-requirements.md\|niche-visual-rules.yaml" "$AGENT"
}

@test "niche-analyst lists visual-requirements.md in outputs" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "stage-gates 01a includes visual_requirements_md hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "visual_requirements_md\|visual-requirements.md" "$GATES"
}

@test "client-assets-collector reads visual-requirements.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/client-assets-collector.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "moodboard-composer reads visual-requirements.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/moodboard-composer.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "references-curator reads visual-requirements.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/references-curator.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "wp-builder has visual sanity-checks section" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/wp-builder.md"
  grep -q "visual-requirements.md\|Visual sanity" "$AGENT"
}

@test "template 01a README mentions visual-requirements.md" {
  README="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template/01a_АНАЛИЗ_НИШИ" && pwd)/README.md"
  grep -q "visual-requirements.md" "$README"
}

@test "stage-gates 01a includes market_profile_md hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "market_profile_md\|market-profile.md" "$GATES"
}

@test "stage-gates 01a includes market_profile_schema validator" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "validate-market-profile.py" "$GATES"
}

@test "stage-gates 01a includes positioning_schema validator" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "validate-positioning.py" "$GATES"
}

@test "stage-gates 01a includes landing_structure_md hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "landing_structure_md\|landing-structure.md" "$GATES"
}

@test "stage-gates 01a includes landing_structure_schema validator" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "validate-landing-structure.py" "$GATES"
}
