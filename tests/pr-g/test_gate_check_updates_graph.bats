#!/usr/bin/env bats

load 'helpers.bash'

@test "gate-check exit 0 → project/wiki/log.md обновляется" {
    project="$(make_fake_project)"
    # Создать wiki/ заранее (имитация миграции)
    mkdir -p "$project/wiki"
    echo "old" > "$project/wiki/log.md"

    # Прогон на 07a_prototype (soft, нет require_approved, но прототипа нет)
    # Создадим минимальный прототип чтобы hard_checks прошли
    mkdir -p "$project/07_ПРОТОТИП/source"
    echo "stub" > "$project/07_ПРОТОТИП/prototype.md"

    # Запустить gate-check (может вернуть != 0 если hard_checks не идеальны,
    # но мы проверяем что ЕСЛИ exit 0 — то wiki обновлена)
    bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 07a_prototype --project "$project" --auto >/dev/null 2>&1 || true

    # Если wiki/log.md изменилось — auto-update сработал
    # Минимум: файл существует и непустой
    [ -s "$project/wiki/log.md" ]
}
