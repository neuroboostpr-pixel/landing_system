#!/usr/bin/env bats
load 'helpers.bash'

@test "take-screenshots.py создаёт desktop + mobile PNG" {
    tmpdir="$(make_minimal_html)"
    run python3 "$PR_I_B_REPO_ROOT/skills/visual-qa/scripts/take-screenshots.py" \
        "$tmpdir/composed.html" --out "$tmpdir/shots/"
    [ "$status" -eq 0 ]
    [ -s "$tmpdir/shots/desktop.png" ]
    [ -s "$tmpdir/shots/mobile.png" ]
}
