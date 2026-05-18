#!/usr/bin/env bats
load 'helpers.bash'

@test "interactive-slot-fill --help выводит usage" {
    # Скрипт может не существовать на момент теста — тогда тест skip
    if [ ! -f "$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/interactive-slot-fill.py" ]; then
        skip "interactive-slot-fill.py не создан (Task 8)"
    fi
    run python3 "$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/interactive-slot-fill.py" --help
    [ "$status" -eq 0 ]
}
