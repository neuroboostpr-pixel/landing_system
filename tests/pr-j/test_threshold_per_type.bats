#!/usr/bin/env bats
load 'helpers.bash'

@test "identity-check: identical images → exit 0 для portrait (threshold 5)" {
    tmpdir=$(mktemp -d)
    make_dummy_jpg "$tmpdir/a.jpg"
    cp "$tmpdir/a.jpg" "$tmpdir/b.jpg"
    run python3 "$PR_J_REPO_ROOT/skills/photo-curation/scripts/identity-check.py" \
        "$tmpdir/a.jpg" "$tmpdir/b.jpg" --slot-type portrait
    [ "$status" -eq 0 ]
    [[ "$output" == *"threshold: 5"* ]]
}

@test "identity-check: identical images → exit 0 для vehicle (threshold 10)" {
    tmpdir=$(mktemp -d)
    make_dummy_jpg "$tmpdir/a.jpg"
    cp "$tmpdir/a.jpg" "$tmpdir/b.jpg"
    run python3 "$PR_J_REPO_ROOT/skills/photo-curation/scripts/identity-check.py" \
        "$tmpdir/a.jpg" "$tmpdir/b.jpg" --slot-type vehicle
    [ "$status" -eq 0 ]
    [[ "$output" == *"threshold: 10"* ]]
}

@test "identity-check: --threshold override побеждает --slot-type" {
    tmpdir=$(mktemp -d)
    make_dummy_jpg "$tmpdir/a.jpg"
    cp "$tmpdir/a.jpg" "$tmpdir/b.jpg"
    run python3 "$PR_J_REPO_ROOT/skills/photo-curation/scripts/identity-check.py" \
        "$tmpdir/a.jpg" "$tmpdir/b.jpg" --slot-type vehicle --threshold 3
    [ "$status" -eq 0 ]
    [[ "$output" == *"threshold: 3"* ]]
}
