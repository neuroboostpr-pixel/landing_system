#!/usr/bin/env bats
# PR-O: generate-blocks.py пропускает блок если slug-папка уже существует,
# и корректно генерирует blocks при мок-codex.

PR_O_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
GENERATE="$PR_O_REPO_ROOT/scripts/import-blocks/generate-blocks.py"
UPDATE_CATALOG="$PR_O_REPO_ROOT/scripts/import-blocks/update-catalog.py"

setup() {
    TMP="$(mktemp -d)"
    LIB="$TMP/block-library"
    WORK="$TMP/work"
    mkdir -p "$LIB" "$WORK"

    # structure.json с одним блоком
    cat > "$WORK/structure.json" <<'JSON'
{
  "page_style_summary": "Test",
  "color_palette": ["#000"],
  "typography_impression": "sans-serif",
  "blocks": [
    {
      "type": "hero",
      "style_mood": "minimal",
      "description": "Test hero",
      "layout_pattern": "split",
      "has_image": true,
      "has_animation": false,
      "niches_suitable": ["services"]
    }
  ]
}
JSON

    # фейковый screenshot
    printf '\x89PNG\r\n\x1a\n' > "$WORK/screen.png"

    # Mock codex: возвращает корректные fenced HTML+CSS
    BIN="$TMP/bin"
    mkdir -p "$BIN"
    cat > "$BIN/codex" <<'BASH'
#!/usr/bin/env bash
cat >/dev/null
cat <<'OUT'
```html
<section class="lp-hero-minimal-split" aria-labelledby="lp-h">
  <h1 id="lp-h">{{slot:headline}}</h1>
  <p>{{slot:subhead}}</p>
  <a class="cta" href="{{slot:cta-href}}">{{slot:cta-label}}</a>
  <img src="{{slot:hero-image}}" alt="{{slot:hero-image-alt}}" loading="lazy">
</section>
```
```css
.lp-hero-minimal-split {
  display: grid;
  gap: var(--lp-spacing-md);
  padding: var(--lp-spacing-xl);
  background: var(--lp-bg);
  color: var(--lp-text);
}
@media (min-width: 768px) {
  .lp-hero-minimal-split { grid-template-columns: 1fr 1fr; }
}
```
OUT
BASH
    chmod +x "$BIN/codex"
    export PATH="$BIN:$PATH"
}

teardown() {
    rm -rf "$TMP"
}

@test "generate-blocks: создаёт блок при первом запуске" {
    run python3 "$GENERATE" \
        --structure "$WORK/structure.json" \
        --screenshot "$WORK/screen.png" \
        --niche "generic" \
        --source-url "https://example.com" \
        --out "$LIB" \
        --work-dir "$WORK"
    [ "$status" -eq 0 ]
    # должна быть создана папка с блоком
    found=$(find "$LIB/hero" -name "meta.yaml" | wc -l | tr -d ' ')
    [ "$found" -eq 1 ]
    # added-blocks.json содержит один блок
    count=$(python3 -c "import json; print(len(json.load(open('$WORK/added-blocks.json'))))")
    [ "$count" -eq 1 ]
}

@test "generate-blocks: пропускает существующий slug при повторном запуске" {
    # 1-й запуск
    python3 "$GENERATE" --structure "$WORK/structure.json" --screenshot "$WORK/screen.png" \
        --niche "generic" --source-url "https://example.com" --out "$LIB" --work-dir "$WORK" >/dev/null
    # 2-й запуск с тем же URL → тот же slug → должен пропустить
    run python3 "$GENERATE" --structure "$WORK/structure.json" --screenshot "$WORK/screen.png" \
        --niche "generic" --source-url "https://example.com" --out "$LIB" --work-dir "$WORK"
    [ "$status" -eq 0 ]
    # added-blocks.json теперь пустой (всё уже было)
    count=$(python3 -c "import json; print(len(json.load(open('$WORK/added-blocks.json'))))")
    [ "$count" -eq 0 ]
    # папка одна, не дублировалась
    found=$(find "$LIB/hero" -name "meta.yaml" | wc -l | tr -d ' ')
    [ "$found" -eq 1 ]
}

@test "update-catalog: добавляет импортированные блоки в catalog.yaml" {
    python3 "$GENERATE" --structure "$WORK/structure.json" --screenshot "$WORK/screen.png" \
        --niche "generic" --source-url "https://example.com" --out "$LIB" --work-dir "$WORK" >/dev/null
    run python3 "$UPDATE_CATALOG" --library "$LIB" --added-from "$WORK/added-blocks.json"
    [ "$status" -eq 0 ]
    [ -f "$LIB/catalog.yaml" ]
    run grep -c "hero-minimal-split" "$LIB/catalog.yaml"
    [ "$status" -eq 0 ]
}
