#!/usr/bin/env bash
# Хелперы для bats-тестов PR-G.

# Корень репо
PR_G_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Создать минимальный fake-проект-лендинг в tmpdir и вернуть путь.
make_fake_project() {
    local tmpdir
    tmpdir=$(mktemp -d)
    cat > "$tmpdir/.landing-state.yaml" <<EOF
project: "test-project"
schema_version: 2
stages:
  "00_brief": {status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "01a_niche_analysis": {status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "03_references": {status: locked, timestamp: ""}
  "04_brand": {status: locked, timestamp: ""}
  "05_design": {status: locked, timestamp: ""}
  "07c_composed": {status: locked, timestamp: ""}
  "07d_photos": {status: locked, timestamp: ""}
  "07e_visuals": {status: locked, timestamp: ""}
  "07f_composed_final": {status: locked, timestamp: ""}
  "07_content": {status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "07a_prototype": {status: locked, timestamp: ""}
  "08_build": {status: locked, timestamp: ""}
  "09_deploy": {status: locked, timestamp: ""}
  "10_qa": {status: locked, timestamp: ""}
EOF
    mkdir -p "$tmpdir/00_БРИФ"
    echo "fake brief" > "$tmpdir/00_БРИФ/brief.md"
    echo "$tmpdir"
}

# Установить status для одного stage в state.yaml
set_status() {
    local project="$1" stage="$2" status="$3"
    yq -i ".stages.\"$stage\".status = \"$status\"" "$project/.landing-state.yaml"
}
