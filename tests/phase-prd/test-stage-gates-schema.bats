#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
GATES="$REPO/config/stage-gates.yaml"

# Extract the block for a given stage key (from its header line until the next top-level key)
extract_stage() {
    local key="$1"
    awk "/^  \"${key}\":/{flag=1; print; next} flag && /^  \"[^\"]+\":/{flag=0} flag{print}" "$GATES"
}

@test "stage-gates.yaml has 7 new PR-D stages defined" {
    for s in "07a_prototype" "07b_wireframe" "07c_composed" "07d_photos" "07e_visuals" "07f_composed_final"; do
        grep -q "^  \"$s\":" "$GATES" || {
            echo "Missing stage gate: $s"; return 1
        }
    done
}

@test "07a_prototype gate checks for prototype.yaml" {
    grep -A 30 '"07a_prototype":' "$GATES" | grep -q "prototype.yaml"
}

@test "07d_photos requires 07c_composed approved" {
    extract_stage "07d_photos" | grep -q '"07c_composed"'
}

@test "07e_visuals also requires 07c_composed (parallel with 07d)" {
    extract_stage "07e_visuals" | grep -q '"07c_composed"'
}

@test "07f_composed_final requires both 07d_photos and 07e_visuals" {
    body="$(extract_stage "07f_composed_final")"
    echo "$body" | grep -q "07d_photos"
    echo "$body" | grep -q "07e_visuals"
}

@test "08_build has theme_php_syntax_valid check" {
    extract_stage "08_build" | grep -q "theme_php_syntax_valid"
}

@test "09_deploy has site_url_accessible check" {
    extract_stage "09_deploy" | grep -q "site_url_accessible"
}

@test "stage-gates.yaml is valid YAML" {
    python3 -c "import yaml; yaml.safe_load(open('$GATES').read())"
}
