#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
ORCH="$REPO/agents/landing-orchestrator.md"

@test "orchestrator references /landing-go command" {
    grep -q "/landing-go" "$ORCH"
}

@test "orchestrator has dispatch table for new PR-A/B/C/D stages" {
    grep -qE "07a_prototype|Прототип \(parse\)" "$ORCH"
    grep -qE "07d_photos|photo-curator" "$ORCH"
    grep -qE "07e_visuals|visual-curator" "$ORCH"
}

@test "orchestrator documents parallel 07d ⇆ 07e dispatch" {
    grep -qE "паралл|parallel|одновременно" "$ORCH"
}

@test "orchestrator documents auto-fix mechanism" {
    grep -qE "auto.?fix|автофикс|авто-fix" "$ORCH"
}

@test "orchestrator documents prototype-first flow with n/a for 00/01/01a/02" {
    grep -qE "prototype.?first|n/a|prototype-first" "$ORCH"
}

@test "orchestrator references derive-landing-structure bridge" {
    grep -q "derive-landing-structure" "$ORCH"
}
