#!/usr/bin/env bats
# PR-O: codex-analyze-structure.sh с мок-codex возвращает валидный JSON.

PR_O_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
ANALYZE="$PR_O_REPO_ROOT/scripts/import-blocks/codex-analyze-structure.sh"
TEMPLATE="$PR_O_REPO_ROOT/scripts/import-blocks/templates/structure-analysis-prompt.md"

setup() {
    TMP="$(mktemp -d)"
    BIN="$TMP/bin"
    mkdir -p "$BIN"
    # Создаём пустой PNG (1x1, минимальный заголовок) — содержимое неважно, codex замокан
    printf '\x89PNG\r\n\x1a\n' > "$TMP/fake.png"

    # Mock codex: игнорит stdin, печатает fenced JSON со структурой
    cat > "$BIN/codex" <<'BASH'
#!/usr/bin/env bash
cat >/dev/null
cat <<'JSON'
```json
{
  "page_style_summary": "Минималистичный editorial landing с крупной типографикой",
  "color_palette": ["#0a0a0a", "#f4f4f4", "#cc8844"],
  "typography_impression": "mixed",
  "blocks": [
    {"type":"hero","style_mood":"editorial","description":"Крупный заголовок и фоновое фото","layout_pattern":"split","has_image":true,"has_animation":false,"niches_suitable":["premium-auto","luxury"]},
    {"type":"features","style_mood":"minimal","description":"Трёхколоночный блок с иконками","layout_pattern":"grid-3","has_image":false,"has_animation":false,"niches_suitable":["services","b2b-saas"]}
  ]
}
```
JSON
BASH
    chmod +x "$BIN/codex"
    export PATH="$BIN:$PATH"
    export CODEX_BIN="$BIN/codex"
}

teardown() {
    rm -rf "$TMP"
}

@test "codex-analyze-structure: возвращает валидный JSON с блоками" {
    [ -f "$TEMPLATE" ]
    run bash "$ANALYZE" "$TMP/fake.png"
    [ "$status" -eq 0 ]
    echo "$output" > "$TMP/out.json"
    run python3 -c "import json,sys; d=json.load(open('$TMP/out.json')); assert len(d['blocks'])==2; assert d['blocks'][0]['type']=='hero'; print('ok')"
    [ "$status" -eq 0 ]
}

@test "codex-analyze-structure: падает если скриншот не существует" {
    run bash "$ANALYZE" "$TMP/nope.png"
    [ "$status" -ne 0 ]
}

@test "codex-analyze-structure: падает без screenshot аргумента" {
    run bash "$ANALYZE"
    [ "$status" -ne 0 ]
}
