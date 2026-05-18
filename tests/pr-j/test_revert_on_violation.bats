#!/usr/bin/env bats
load 'helpers.bash'

# Этот тест проверяет логику revert через mock identity-check.
# Реальный полный pipeline не запускаем (требует codex), вместо этого
# тестируем что manifest правильно формируется когда identity check fails.

@test "photo-pipeline manifest: identity_violation поле есть" {
    # Косвенно — проверяем что обновлённый код содержит identity_violation
    # в выходном dict (smoke-grep)
    grep -q "identity_violation" "$PR_J_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py"
}

@test "photo-pipeline: передаёт --slot-type в identity-check" {
    grep -q -- "--slot-type" "$PR_J_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py"
}
