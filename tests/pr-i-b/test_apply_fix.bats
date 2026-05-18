#!/usr/bin/env bats
load 'helpers.bash'

@test "apply-fix.py: блокирует text_* типы" {
    tmpdir="$(make_minimal_html)"
    run python3 "$PR_I_B_REPO_ROOT/skills/visual-qa/scripts/apply-fix.py" \
        "$tmpdir/composed.html" \
        --issue '{"type":"text_overflow","selector":"h1","fix_hint":"truncate"}'
    [ "$status" -eq 3 ]
    [[ "$output" == *"BLOCKED"* ]] || [[ "$output" == *"запрещ"* ]]
}

@test "apply-fix.py: css_tweak применяется на selector" {
    tmpdir="$(make_minimal_html)"
    run python3 "$PR_I_B_REPO_ROOT/skills/visual-qa/scripts/apply-fix.py" \
        "$tmpdir/composed.html" \
        --issue '{"type":"css_tweak","selector":"h1","fix_hint":"color: red"}'
    [ "$status" -eq 0 ]
    grep -q "color: red" "$tmpdir/composed.html"
}
