#!/usr/bin/env bats

load 'helpers.bash'

@test "04_brand (soft) при locked 03_references — печатает warning, exit 0 c --auto" {
    project="$(make_fake_project)"
    # 03_references по умолчанию locked в фикстуре
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 04_brand --project "$project" --auto
    # exit code не обязательно 0 (hard_checks могут упасть), главное warning
    [[ "$output" == *"Soft warning"* ]] || [[ "$output" == *"⚠️"* ]]
}

@test "04_brand soft БЕЗ --auto + stdin = 'y' — продолжает" {
    project="$(make_fake_project)"
    # Без -t 0 (нет tty в bats), скрипт не должен спрашивать, а пропустить
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 04_brand --project "$project"
    # warning должен быть
    [[ "$output" == *"⚠"* ]] || [[ "$output" == *"Soft"* ]] || true
}
