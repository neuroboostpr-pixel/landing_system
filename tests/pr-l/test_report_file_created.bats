#!/usr/bin/env bats
load 'helpers.bash'

# Проверка что 10_QA/final-check-report.md создаётся и содержит секции.

setup() {
    SANDBOX="$(pr_l_make_sandbox 0 0 0 0 0 0)"
    PROJECT="$(pr_l_make_project)"
}

teardown() {
    rm -rf "$SANDBOX" "$PROJECT"
}

@test "final-check: создаёт 10_QA/final-check-report.md" {
    run bash "$SANDBOX/scripts/landing-final-check.sh" "$PROJECT"
    [ -f "$PROJECT/10_QA/final-check-report.md" ]
}

@test "final-check: отчёт содержит все 6 секций проверок" {
    bash "$SANDBOX/scripts/landing-final-check.sh" "$PROJECT" || true
    local report="$PROJECT/10_QA/final-check-report.md"
    [ -f "$report" ]
    grep -q "### wiki-sync" "$report"
    grep -q "### composed-premium" "$report"
    grep -q "### content-preserved" "$report"
    grep -q "### photo-pipeline" "$report"
    grep -q "### identity-preserved" "$report"
    grep -q "### visual-qa" "$report"
}

@test "final-check: итог в отчёте — ВСЕ обязательные проверки прошли" {
    bash "$SANDBOX/scripts/landing-final-check.sh" "$PROJECT" || true
    grep -q "ВСЕ обязательные проверки прошли" "$PROJECT/10_QA/final-check-report.md"
}
