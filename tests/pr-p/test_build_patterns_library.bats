#!/usr/bin/env bats
# PR-P: build-patterns-library.py создаёт reusable снипеты
# (папки с index.html / styles.css / meta.yaml) из findings.json.

PR_P_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
BUILD="$PR_P_REPO_ROOT/scripts/extract-effects/build-patterns-library.py"

setup() {
    TMP="$(mktemp -d)"
    PATTERNS_OUT="$TMP/_patterns"
    mkdir -p "$PATTERNS_OUT"

    # findings.json фикстура
    cat > "$TMP/findings.json" <<'JSON'
{
  "keyframes": ["fadeIn", "pulseGlow", "slideUp"],
  "hover_states": [
    [".btn-primary", "transform: translateY(-3px);"],
    [".card", "box-shadow: 0 12px 40px rgba(0,0,0,0.3);"]
  ],
  "backdrop_filter": ["blur(20px) saturate(180%)"],
  "gradient_complex": ["linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #48dbfb 100%)"]
}
JSON

    export PATTERNS_DIR_OVERRIDE="$PATTERNS_OUT"
}

teardown() {
    rm -rf "$TMP"
    unset PATTERNS_DIR_OVERRIDE
}

@test "build-patterns-library: создаёт папки в _patterns/" {
    run python3 "$BUILD" "$TMP/findings.json"
    [ "$status" -eq 0 ]
    # Должна появиться хотя бы одна папка-паттерн
    cnt=$(find "$PATTERNS_OUT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
    [ "$cnt" -gt 0 ]
}

@test "build-patterns-library: каждая папка содержит index.html, styles.css, meta.yaml" {
    python3 "$BUILD" "$TMP/findings.json"
    while IFS= read -r d; do
        [ -f "$d/index.html" ] || { echo "missing index.html in $d"; return 1; }
        [ -f "$d/styles.css" ] || { echo "missing styles.css in $d"; return 1; }
        [ -f "$d/meta.yaml" ]  || { echo "missing meta.yaml in $d";  return 1; }
    done < <(find "$PATTERNS_OUT" -mindepth 1 -maxdepth 1 -type d)
}

@test "build-patterns-library: создаёт hover, animation, glass и gradient паттерны" {
    python3 "$BUILD" "$TMP/findings.json"
    ls "$PATTERNS_OUT" | grep -q "^hover-effect-"
    ls "$PATTERNS_OUT" | grep -q "^animation-"
    ls "$PATTERNS_OUT" | grep -q "^glass-"
    ls "$PATTERNS_OUT" | grep -q "^gradient-mesh-"
}

@test "build-patterns-library: meta.yaml содержит обязательные поля" {
    python3 "$BUILD" "$TMP/findings.json"
    first=$(find "$PATTERNS_OUT" -name "meta.yaml" | head -1)
    [ -n "$first" ]
    grep -q "^id:" "$first"
    grep -q "^type: pattern" "$first"
    grep -q "^import_method: css-pattern-extraction" "$first"
}

@test "build-patterns-library: повторный запуск не дублирует существующие" {
    python3 "$BUILD" "$TMP/findings.json" >/dev/null
    before=$(find "$PATTERNS_OUT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
    # Второй прогон с тем же findings.json
    run python3 "$BUILD" "$TMP/findings.json"
    [ "$status" -eq 0 ]
    after=$(find "$PATTERNS_OUT" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
    [ "$before" = "$after" ]
}
