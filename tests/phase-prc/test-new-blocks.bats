#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "ru-features-XX-kpi-metrics block exists with valid structure" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    [ -n "$BLOCK" ]
    [ -f "$BLOCK/meta.yaml" ]
    [ -f "$BLOCK/assets/template.html" ]
    [ -f "$BLOCK/assets/template-mobile.html" ]
    [ -f "$BLOCK/SKILL.md" ]
}

@test "kpi-metrics meta.yaml has type=infographic slots" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    grep -q "type: infographic" "$BLOCK/meta.yaml"
}

@test "kpi-metrics has chart_type field" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    grep -qE "chart_type:|chart_type " "$BLOCK/meta.yaml"
}

@test "ru-stats-XX-growth-chart block exists with valid structure" {
    BLOCK="$(ls -d "$REPO/block-library/social-proof/ru-stats-"*"-growth-chart" 2>/dev/null | head -1)"
    [ -n "$BLOCK" ]
    [ -f "$BLOCK/meta.yaml" ]
    [ -f "$BLOCK/assets/template.html" ]
}

@test "growth-chart meta.yaml has type=infographic line slot" {
    BLOCK="$(ls -d "$REPO/block-library/social-proof/ru-stats-"*"-growth-chart" 2>/dev/null | head -1)"
    grep -q "type: infographic" "$BLOCK/meta.yaml"
    grep -qE "chart_type:.*line|line.*chart_type" "$BLOCK/meta.yaml"
}

@test "template.html files have data-slot-type=infographic" {
    BLOCK="$(ls -d "$REPO/block-library/features/ru-features-"*"-kpi-metrics" 2>/dev/null | head -1)"
    grep -q 'data-slot-type="infographic"' "$BLOCK/assets/template.html"
}
