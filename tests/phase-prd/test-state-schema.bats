#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
STATE="$REPO/template/.landing-state.yaml"

@test "state.yaml has all 7 new PR-A/B/C/D stages" {
    for s in "07a_prototype" "07b_wireframe" "07c_composed" "07d_photos" "07e_visuals" "07f_composed_final"; do
        grep -q "\"$s\":" "$STATE" || {
            echo "Missing stage: $s"; return 1
        }
    done
}

@test "upstream stages (00/01/01a/02) default to 'locked', not 'n/a'" {
    # Phase 3 (audit M5): upstream stages default to "locked" so that
    # /landing-go or /landing-start must explicitly flip them to "n/a"
    # for prototype-first flow. Previous default of "n/a" silently
    # bypassed 14 hard-checks of niche-analysis (audit gap).
    grep -E '"00_brief":\s*\{status:\s*locked' "$STATE"
    grep -E '"01_context":\s*\{status:\s*locked' "$STATE"
    grep -E '"01a_niche_analysis":\s*\{status:\s*locked' "$STATE"
    grep -E '"02_assets":\s*\{status:\s*locked' "$STATE"
}

@test "07a_prototype is the new entry stage with in_progress status" {
    grep -E '"07a_prototype":\s*\{status:\s*in_progress' "$STATE"
}

@test "state.yaml is valid YAML" {
    python3 -c "import yaml; yaml.safe_load(open('$STATE').read())"
}
