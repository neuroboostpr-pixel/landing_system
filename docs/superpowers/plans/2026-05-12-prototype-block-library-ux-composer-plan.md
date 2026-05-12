# PR-A: Prototype + Block Library + ux-composer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Дать landing-system явный артефакт «Прототип», общую block-library с 17 RU-блоками и трёхэтапный конвейер `/landing-prototype` → `/landing-wireframe` → `/landing-compose` для сборки макета между Design.md и кодом.

**Architecture:** Три новых агента (prototype-importer, ux-composer, block-composer) + четыре skill-обёртки (prototype-import, block-library-management, wireframe-rendering, block-composition) + три slash-команды. Block library живёт в `landing-system/block-library/`, формат блока заимствован у OpenDesign (SKILL.md + assets/template.html + assets/template-mobile.html + meta.yaml). Project-side артефакты складываются в новые папки `07_ПРОТОТИП`, `07a_WIREFRAME`, `07b_COMPOSED` внутри project template. ux-composer работает через pre-flight injection — никаких «придумываний», только выбор из библиотеки.

**Tech Stack:** Python 3.10+ (валидаторы, рендерёры, парсеры) · bash (CLI обёртки) · bats + pytest (тесты) · PyYAML · pypdf / pdfminer.six (PDF parsing) · vanilla HTML/CSS (блоки + wireframe, CSS-only переключатели через `:checked`) · OpenDesign extracts (Apache-2.0).

**Spec:** [`docs/superpowers/specs/2026-05-12-prototype-block-library-ux-composer-design.md`](../specs/2026-05-12-prototype-block-library-ux-composer-design.md)

---

## File Structure

Все пути относительно `landing-system/`.

### Создаём новые

```
block-library/
  README.md
  catalog.yaml
  references/.gitkeep
  hero/                              ← seed-блоки (Task 10)
    ru-hero-01-services-calc/
      SKILL.md
      assets/template.html
      assets/template-mobile.html
      meta.yaml
    ru-hero-02-b2c-expert/
    ru-hero-03-local-interior/
  features/, social-proof/, process/, pricing/, trust/, cta/, faq/, quiz/

vendor/opendesign-extracts/
  LICENSE                            ← копия Apache-2.0
  ATTRIBUTION.md                     ← список взятого + commit hash
  README.md                          ← как обновлять
  prompt-templates/.gitkeep          ← пустой stub (наполнение в PR-C)
  design-systems-refs/.gitkeep       ← пустой stub (наполнение postponed)
  skill-block-template/
    SKILL.md                         ← шаблон для копирования при создании блока
    assets/template.html
    assets/template-mobile.html
    meta.yaml
  device-frames/.gitkeep             ← пустой stub

THIRD_PARTY_NOTICES.md                ← общий attribution файл

skills/prototype-import/
  SKILL.md
  scripts/extract-pdf-text.py
  scripts/md-to-yaml.py
  scripts/validate-prototype.py

skills/block-library-management/
  SKILL.md
  scripts/validate-catalog.py
  scripts/validate-meta.py
  scripts/scaffold-block.py

skills/wireframe-rendering/
  SKILL.md
  scripts/match-candidates.py
  scripts/render-wireframe.py
  scripts/serve-preview.sh
  templates/wireframe-shell.html

skills/block-composition/
  SKILL.md
  scripts/inject-tokens.py
  scripts/inject-content.py
  scripts/compose-blocks.py
  scripts/validate-selections.py

agents/prototype-importer.md
agents/ux-composer.md
agents/block-composer.md

commands/landing-prototype.md
commands/landing-wireframe.md
commands/landing-compose.md

template/07_ПРОТОТИП/.gitkeep
template/07_ПРОТОТИП/source/.gitkeep
template/07a_WIREFRAME/.gitkeep
template/07b_COMPOSED/.gitkeep

tests/phase-pra/
  test-validate-catalog.bats
  test-validate-meta.bats
  test-validate-prototype.bats
  test-validate-selections.bats
  test-scaffold-block.bats
  test-extract-pdf-text.bats
  test-md-to-yaml.bats
  test-match-candidates.bats
  test-render-wireframe.bats
  test-inject-tokens.bats
  test-inject-content.bats
  test-compose-blocks.bats
  test-seed-blocks.bats
  fixtures/
    prototype-sample.md
    prototype-sample.pdf            ← bin file, ~1-2 страницы
    tokens-sample.json
    selections-sample.yaml
    catalog-valid.yaml
    catalog-duplicate-id.yaml
    meta-valid.yaml
    meta-missing-slots.yaml
```

### Модифицируем существующие

- `package.json` — добавить script `test:phase-pra`
- `CLAUDE.md` — упомянуть новые команды и стадии
- `skills/design-tokens-generation/SKILL.md` — обновить под 9-секционную DESIGN.md структуру (Task 26)
- `skills/design-tokens-generation/scripts/generate-design-md.py` — добавить новые секции в шаблон

### НЕ модифицируем (зона PR-D)

- `agents/landing-orchestrator.md`
- `config/stage-gates.yaml`
- `template/.landing-state.yaml` (если есть)
- `scripts/gate-check.sh`

---

## Phase 0 — Foundation

### Task 1: Scaffold project-template новые этапные папки

**Files:**
- Create: `template/07_ПРОТОТИП/.gitkeep`
- Create: `template/07_ПРОТОТИП/source/.gitkeep`
- Create: `template/07a_WIREFRAME/.gitkeep`
- Create: `template/07b_COMPOSED/.gitkeep`
- Create: `template/07_ПРОТОТИП/README.md`
- Create: `template/07a_WIREFRAME/README.md`
- Create: `template/07b_COMPOSED/README.md`

- [ ] **Step 1: Создать папки и .gitkeep**

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p template/07_ПРОТОТИП/source template/07a_WIREFRAME template/07b_COMPOSED
touch template/07_ПРОТОТИП/.gitkeep \
      template/07_ПРОТОТИП/source/.gitkeep \
      template/07a_WIREFRAME/.gitkeep \
      template/07b_COMPOSED/.gitkeep
```

- [ ] **Step 2: README.md в 07_ПРОТОТИП**

Содержимое `template/07_ПРОТОТИП/README.md`:
```markdown
# 07 Прототип

Сюда складывается прототип-источник правды от клиента/маркетолога.

## Структура

- `source/prototype.pdf` (или `.md`) — исходник от пользователя
- `prototype.md` — человеко-читаемая нормализация (генерируется `/landing-prototype`)
- `prototype.yaml` — машинно-читаемая версия для `ux-composer`
- `import-log.md` — что агент понял / какие задавал уточняющие вопросы

## Workflow

1. Положи PDF или MD в `source/`.
2. Запусти `/landing-prototype`.
3. Проверь сгенерированный `prototype.md`. Правки вноси в него — `prototype.yaml` перегенерится автоматически.
```

- [ ] **Step 3: README.md в 07a_WIREFRAME**

Содержимое:
```markdown
# 07a Wireframe

Интерактивный preview с выбором композиций блоков. Артефакты:

- `wireframe.html` — desktop+mobile preview, radio-кнопки для каждого блока
- `candidates.yaml` — 2-3 кандидата на блок (выход `ux-composer`)
- `selections.yaml` — финальный выбор пользователя

## Открыть preview

Двойной клик по `wireframe.html` (radio-кнопки работают on `file://`).
Если iframe-preview не рендерится — запусти helper:

```
bash skills/wireframe-rendering/scripts/serve-preview.sh 07a_WIREFRAME/
```

После выбора — нажми кнопку «Confirm selections» внизу и сохрани файл `selections.yaml`.
```

- [ ] **Step 4: README.md в 07b_COMPOSED**

Содержимое:
```markdown
# 07b Composed

Цветной макет с наложенной дизайн-системой и реальными текстами/CTA из прототипа.
Места для финального визуального контента (фото/иконки/инфографика) показаны
как явные placeholders с описаниями слотов.

- `composed.html` — desktop сборка
- `composed-mobile.html` — mobile сборка
- `block-injection-log.md` — лог что куда подставлено

Этот артефакт — пред-финальный. Финальный визуал добавит PR-B (Photo Pipeline) и PR-C (Icon/Infographic generators).
```

- [ ] **Step 5: Commit**

```bash
git add template/07_ПРОТОТИП template/07a_WIREFRAME template/07b_COMPOSED
git commit -m "feat(template): scaffold 07_ПРОТОТИП, 07a_WIREFRAME, 07b_COMPOSED stage folders"
```

---

### Task 2: Scaffold block-library + catalog seed

**Files:**
- Create: `block-library/README.md`
- Create: `block-library/catalog.yaml`
- Create: `block-library/references/.gitkeep`
- Create: `block-library/hero/.gitkeep`
- Create: `block-library/features/.gitkeep`
- Create: `block-library/social-proof/.gitkeep`
- Create: `block-library/process/.gitkeep`
- Create: `block-library/pricing/.gitkeep`
- Create: `block-library/trust/.gitkeep`
- Create: `block-library/cta/.gitkeep`
- Create: `block-library/faq/.gitkeep`
- Create: `block-library/quiz/.gitkeep`

- [ ] **Step 1: Создать структуру папок**

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p block-library/{references,hero,features,social-proof,process,pricing,trust,cta,faq,quiz}
for d in references hero features social-proof process pricing trust cta faq quiz; do
  touch "block-library/$d/.gitkeep"
done
```

- [ ] **Step 2: Создать `block-library/README.md`**

Содержимое:
```markdown
# Block Library

Общая библиотека wireframe-блоков для всех проектов landing-system.

## Структура одного блока

```
hero/ru-hero-01-services-calc/
  SKILL.md              ← когда применять, slots, conversion-notes
  assets/
    template.html       ← desktop wireframe (ч/б), CSS внутри <style>
    template-mobile.html
  meta.yaml             ← schema: см. skills/block-library-management/scripts/validate-meta.py
```

## Категории

- `hero/`, `features/`, `social-proof/`, `process/`, `pricing/`, `trust/`, `cta/`, `faq/`, `quiz/`

## Naming convention

`<market>-<category>-<NN>-<descriptor>` в kebab-case. Примеры:
- `ru-hero-01-services-calc`
- `ru-quiz-step-card`

**Иммутабельность:** существующие блоки НЕ редактируются. Изменение = новый id с суффиксом `-v2`, например `ru-hero-01-services-calc-v2`.

## Добавить новый блок

```bash
python skills/block-library-management/scripts/scaffold-block.py \
    --id ru-hero-04-something --category hero
```

Скаффолдер создаст папку, копирует `vendor/opendesign-extracts/skill-block-template/`, обновит `catalog.yaml`.

## Валидация

```bash
python skills/block-library-management/scripts/validate-catalog.py block-library/catalog.yaml
python skills/block-library-management/scripts/validate-meta.py block-library/hero/ru-hero-01-services-calc/meta.yaml
```

## Атрибуция

Формат блоков заимствован у OpenDesign (Apache-2.0). См. `THIRD_PARTY_NOTICES.md`.
```

- [ ] **Step 3: Создать пустой `block-library/catalog.yaml`**

Содержимое:
```yaml
version: 1
updated: 2026-05-12
blocks: []
```

- [ ] **Step 4: Commit**

```bash
git add block-library/
git commit -m "feat(block-library): scaffold directory structure + empty catalog"
```

---

### Task 3: Scaffold vendor/opendesign-extracts + THIRD_PARTY_NOTICES

**Files:**
- Create: `vendor/opendesign-extracts/LICENSE`
- Create: `vendor/opendesign-extracts/ATTRIBUTION.md`
- Create: `vendor/opendesign-extracts/README.md`
- Create: `vendor/opendesign-extracts/prompt-templates/.gitkeep`
- Create: `vendor/opendesign-extracts/design-systems-refs/.gitkeep`
- Create: `vendor/opendesign-extracts/device-frames/.gitkeep`
- Create: `vendor/opendesign-extracts/skill-block-template/SKILL.md`
- Create: `vendor/opendesign-extracts/skill-block-template/assets/template.html`
- Create: `vendor/opendesign-extracts/skill-block-template/assets/template-mobile.html`
- Create: `vendor/opendesign-extracts/skill-block-template/meta.yaml`
- Create: `THIRD_PARTY_NOTICES.md`

- [ ] **Step 1: Скачать Apache-2.0 LICENSE**

```bash
cd "$(git rev-parse --show-toplevel)"
mkdir -p vendor/opendesign-extracts/{prompt-templates,design-systems-refs,device-frames,skill-block-template/assets}
curl -sL "https://www.apache.org/licenses/LICENSE-2.0.txt" -o vendor/opendesign-extracts/LICENSE
touch vendor/opendesign-extracts/prompt-templates/.gitkeep \
      vendor/opendesign-extracts/design-systems-refs/.gitkeep \
      vendor/opendesign-extracts/device-frames/.gitkeep
```

Проверка:
```bash
head -3 vendor/opendesign-extracts/LICENSE
```
Ожидаемо: первая строка содержит `Apache License`.

- [ ] **Step 2: ATTRIBUTION.md**

Содержимое `vendor/opendesign-extracts/ATTRIBUTION.md`:
```markdown
# OpenDesign Extracts — Attribution

**Source:** https://github.com/nexu-io/open-design
**License:** Apache-2.0 (see `LICENSE`)
**Extraction date:** 2026-05-12
**Pinned commit:** TBD-COMMIT-HASH ← обновить после первой реальной выгрузки файлов

## What we use

| Letter | What | Files in this repo | Used by |
|---|---|---|---|
| A | Skill-block format (SKILL.md + assets + meta.yaml) | `skill-block-template/` | `block-library/*` |
| B | 93 prompt-templates for gpt-image-2 | `prompt-templates/` (populate in PR-C) | PR-C icon/infographic generators |
| C | 72 reference DESIGN.md files | `design-systems-refs/` (populate later) | Design-system-generator references |
| D | Pre-flight injection pattern | applied in `ux-composer` mission | ux-composer logic |
| G | 9-section DESIGN.md structure | applied in `design-tokens-generation` skill | DESIGN.md template |
| H | `saas-landing` skill seed | adapted in `block-library/hero/ru-hero-02-b2c-expert` | seed blocks |
| I | Device frames | `device-frames/` (populate later) | wireframe.html mobile preview |
| J | TodoWrite plan streaming pattern | applied in landing-orchestrator (PR-D) | Orchestrator UX |
| K | Sandboxed iframe preview | applied in `wireframe-rendering` skill | wireframe.html iframe |

## NOT used

- Daemon (Node + Express + SQLite) — we don't run a server
- Next.js SPA
- BYOK proxy
```

- [ ] **Step 3: README.md в vendor/opendesign-extracts**

Содержимое:
```markdown
# OpenDesign Extracts

Copy-only extraction. We do NOT vendor the full repo or use git-submodules.

## How to refresh

1. Clone OpenDesign locally: `git clone https://github.com/nexu-io/open-design /tmp/od`
2. Note the commit hash: `git -C /tmp/od rev-parse HEAD`
3. Copy needed files (see `ATTRIBUTION.md` table) with header comment:
   ```
   <!-- Source: github.com/nexu-io/open-design @ <commit-hash> | Licensed: Apache-2.0 -->
   ```
4. Update `ATTRIBUTION.md` `Pinned commit` field.
5. Commit.

## Do not

- Edit copied files. If a file needs changes — fork it into the target location (e.g. `block-library/`) with adapted comment header.
- Add upstream dependencies. Each extract must be standalone (no imports from siblings unless documented).
```

- [ ] **Step 4: Создать skill-block-template (шаблон для копирования)**

`vendor/opendesign-extracts/skill-block-template/SKILL.md`:
```markdown
<!-- Source: github.com/nexu-io/open-design @ <commit-hash> | Licensed: Apache-2.0 -->
<!-- Adapted as block-library skeleton -->
---
name: <block-id>
description: <one-line description>
---

# <block-id>

## Когда применять

<сценарий, ниша, какой блок прототипа этим закрывается>

## Slots

<перечень слотов: photo / text / cta / icon — см. meta.yaml>

## Conversion notes

<почему работает на конверсию, что важно сохранять при кастомизации>

## Mobile considerations

<что отличается в template-mobile.html>
```

`vendor/opendesign-extracts/skill-block-template/assets/template.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>{{block_id}} — desktop wireframe</title>
<style>
  /* Wireframe: ч/б, CSS-only, no external deps.
     CSS vars in :root are MANDATORY — block-composition/inject-tokens.py relies on these names. */
  :root {
    --color-bg: #fff;
    --color-fg: #111;
    --color-accent: #333;
    --color-border: #ccc;
    --font-display: system-ui, sans-serif;
    --font-body: system-ui, sans-serif;
    --spacing-md: 16px;
    --spacing-lg: 32px;
  }
  body { margin: 0; font-family: var(--font-body); background: var(--color-bg); color: var(--color-fg); }
  .slot { border: 2px dashed #999; padding: var(--spacing-md); margin: 8px; background: #f4f4f4; }
  .slot-label { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
  /* Replace this scaffold with real block-specific layout */
</style>
</head>
<body>
  <section class="block-wireframe" data-block-id="{{block_id}}">
    <!-- Replace with block-specific markup -->
    <div class="slot"><div class="slot-label">REPLACE ME</div></div>
  </section>
</body>
</html>
```

`vendor/opendesign-extracts/skill-block-template/assets/template-mobile.html`: тот же шаблон с `width: 375px;` на body.

`vendor/opendesign-extracts/skill-block-template/meta.yaml`:
```yaml
id: <kebab-case-id>
category: <hero|features|social-proof|process|pricing|trust|cta|faq|quiz>
ru_market: true
use_cases: [services, b2c, local]
description: ""
slots: []
conversion_notes: ""
source: manual
source_attribution: ""
created: 2026-05-12
```

- [ ] **Step 5: THIRD_PARTY_NOTICES.md в корне landing-system/**

Содержимое:
```markdown
# Third Party Notices

This product includes software developed by third parties.

## OpenDesign

- **Project:** https://github.com/nexu-io/open-design
- **License:** Apache License 2.0
- **License text:** [`vendor/opendesign-extracts/LICENSE`](vendor/opendesign-extracts/LICENSE)
- **What we use:** see [`vendor/opendesign-extracts/ATTRIBUTION.md`](vendor/opendesign-extracts/ATTRIBUTION.md)

## ui-ux-pro-max (user-local skill)

Pattern engine referenced for landing.csv / web-interface.csv / ux-guidelines.csv.
Source: user's local Claude skill at `~/.claude/skills/ui-ux-pro-max`.

## awesome-design-md (via OpenDesign)

The 72 reference DESIGN.md files in `vendor/opendesign-extracts/design-systems-refs/`
originate from https://github.com/VoltAgent/awesome-design-md.

## anthropic-skills:pdf

Used for PDF parsing in `prototype-import` skill. See `~/.claude/skills/anthropic-skills/pdf`.
```

- [ ] **Step 6: Commit**

```bash
git add vendor/opendesign-extracts THIRD_PARTY_NOTICES.md
git commit -m "feat(vendor): scaffold OpenDesign extracts dir + Apache-2.0 attribution"
```

---

## Phase 1 — Schema validators (TDD)

### Task 4: catalog.yaml validator

**Files:**
- Create: `skills/block-library-management/SKILL.md`
- Create: `skills/block-library-management/scripts/validate-catalog.py`
- Create: `tests/phase-pra/test-validate-catalog.bats`
- Create: `tests/phase-pra/fixtures/catalog-valid.yaml`
- Create: `tests/phase-pra/fixtures/catalog-duplicate-id.yaml`
- Create: `tests/phase-pra/fixtures/catalog-missing-version.yaml`

- [ ] **Step 1: Создать fixtures**

`tests/phase-pra/fixtures/catalog-valid.yaml`:
```yaml
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-01-services-calc
    path: hero/ru-hero-01-services-calc/
    category: hero
    use_cases: [services]
  - id: ru-features-01-3col-icons
    path: features/ru-features-01-3col-icons/
    category: features
    use_cases: [services, b2c, local]
```

`tests/phase-pra/fixtures/catalog-duplicate-id.yaml`:
```yaml
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-01-services-calc
    path: hero/ru-hero-01-services-calc/
    category: hero
    use_cases: [services]
  - id: ru-hero-01-services-calc
    path: hero/ru-hero-01-duplicate/
    category: hero
    use_cases: [b2c]
```

`tests/phase-pra/fixtures/catalog-missing-version.yaml`:
```yaml
blocks: []
```

- [ ] **Step 2: Написать failing bats тест**

`tests/phase-pra/test-validate-catalog.bats`:
```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/block-library-management/scripts/validate-catalog.py"
}

@test "accepts valid catalog" {
  run python3 "$VALIDATOR" "$FIXTURES/catalog-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects catalog with duplicate ids" {
  run python3 "$VALIDATOR" "$FIXTURES/catalog-duplicate-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate id"* ]]
}

@test "rejects catalog missing version" {
  run python3 "$VALIDATOR" "$FIXTURES/catalog-missing-version.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"version"* ]]
}

@test "accepts empty blocks list" {
  cat > "$BATS_TMPDIR/empty.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/empty.yaml"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 3: Запустить тест — должен упасть**

```bash
bats tests/phase-pra/test-validate-catalog.bats
```
Ожидаемо: 4 теста FAIL с "validate-catalog.py not found".

- [ ] **Step 4: Написать минимальный validator**

`skills/block-library-management/scripts/validate-catalog.py`:
```python
#!/usr/bin/env python3
"""Validate block-library/catalog.yaml.

Usage: validate-catalog.py <path-to-catalog.yaml>
Exit 0 on valid, non-zero with explanation on invalid.
"""
import sys
import yaml
from pathlib import Path


REQUIRED_TOP_KEYS = {"version", "updated", "blocks"}
REQUIRED_BLOCK_KEYS = {"id", "path", "category", "use_cases"}
VALID_CATEGORIES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
VALID_USE_CASES = {"services", "b2c", "local"}


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    missing = REQUIRED_TOP_KEYS - set(data.keys())
    if missing:
        fail(f"missing required top-level keys: {sorted(missing)}")
    if not isinstance(data["blocks"], list):
        fail("blocks must be a list")
    seen_ids: set[str] = set()
    for i, block in enumerate(data["blocks"]):
        if not isinstance(block, dict):
            fail(f"block #{i} must be a mapping")
        missing_b = REQUIRED_BLOCK_KEYS - set(block.keys())
        if missing_b:
            fail(f"block #{i} missing keys: {sorted(missing_b)}")
        if block["id"] in seen_ids:
            fail(f"duplicate id: {block['id']}")
        seen_ids.add(block["id"])
        if block["category"] not in VALID_CATEGORIES:
            fail(f"block {block['id']}: invalid category {block['category']!r}")
        for uc in block["use_cases"]:
            if uc not in VALID_USE_CASES:
                fail(f"block {block['id']}: invalid use_case {uc!r}")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-catalog.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
```

- [ ] **Step 5: Создать SKILL.md (минимум для прохождения тестов)**

`skills/block-library-management/SKILL.md`:
```markdown
---
name: block-library-management
description: Manage the shared block-library — scaffold new blocks, validate catalog and per-block meta.yaml schemas. Used by ux-composer at injection time.
---

# block-library-management

Утилиты для управления `block-library/`:

- `scripts/validate-catalog.py <path>` — валидировать `catalog.yaml`
- `scripts/validate-meta.py <path>` — валидировать `meta.yaml` блока
- `scripts/scaffold-block.py --id <id> --category <cat>` — создать новый блок из шаблона

См. также: `block-library/README.md`.
```

- [ ] **Step 6: Запустить тесты — должны пройти**

```bash
bats tests/phase-pra/test-validate-catalog.bats
```
Ожидаемо: 4/4 PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/block-library-management/ tests/phase-pra/test-validate-catalog.bats tests/phase-pra/fixtures/catalog-*.yaml
git commit -m "feat(block-library): validate-catalog.py + bats tests"
```

---

### Task 5: meta.yaml validator

**Files:**
- Create: `skills/block-library-management/scripts/validate-meta.py`
- Create: `tests/phase-pra/test-validate-meta.bats`
- Create: `tests/phase-pra/fixtures/meta-valid.yaml`
- Create: `tests/phase-pra/fixtures/meta-missing-slots.yaml`
- Create: `tests/phase-pra/fixtures/meta-invalid-category.yaml`

- [ ] **Step 1: Fixtures**

`tests/phase-pra/fixtures/meta-valid.yaml`:
```yaml
id: ru-hero-01-services-calc
category: hero
ru_market: true
use_cases: [services]
description: "Hero с фото объекта на фоне + оффер слева + кнопка расчёта"
slots:
  - {type: photo, name: hero-bg, ratio: "16:9", mobile_ratio: "9:16", required: true}
  - {type: text, name: headline, max_chars: 60, required: true}
  - {type: cta, name: primary, default_text: "Рассчитать стоимость", required: true}
conversion_notes: "Sticky CTA, контраст 7:1, плашка 'от X ₽'"
source: manual
source_attribution: ""
created: 2026-05-12
```

`tests/phase-pra/fixtures/meta-missing-slots.yaml`:
```yaml
id: ru-hero-broken
category: hero
ru_market: true
use_cases: [services]
description: "Broken"
source: manual
created: 2026-05-12
```

`tests/phase-pra/fixtures/meta-invalid-category.yaml`:
```yaml
id: ru-something-bad
category: foobar
ru_market: true
use_cases: [services]
description: "Bad category"
slots: []
source: manual
created: 2026-05-12
```

- [ ] **Step 2: bats тест**

`tests/phase-pra/test-validate-meta.bats`:
```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/block-library-management/scripts/validate-meta.py"
}

@test "accepts valid meta" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects meta missing slots key" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-missing-slots.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"slots"* ]]
}

@test "rejects meta with invalid category" {
  run python3 "$VALIDATOR" "$FIXTURES/meta-invalid-category.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"category"* ]]
}

@test "rejects meta with non-kebab-case id" {
  cat > "$BATS_TMPDIR/bad-id.yaml" <<EOF
id: Ru_Hero_01_BadCase
category: hero
ru_market: true
use_cases: [services]
description: "bad id"
slots: []
source: manual
created: 2026-05-12
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/bad-id.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"kebab-case"* ]]
}
```

- [ ] **Step 3: Запустить — должен упасть**

```bash
bats tests/phase-pra/test-validate-meta.bats
```

- [ ] **Step 4: validate-meta.py**

```python
#!/usr/bin/env python3
"""Validate block-library/<category>/<id>/meta.yaml."""
import re
import sys
import yaml
from pathlib import Path

REQUIRED_KEYS = {
    "id", "category", "ru_market", "use_cases",
    "description", "slots", "source", "created",
}
VALID_CATEGORIES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
VALID_USE_CASES = {"services", "b2c", "local"}
VALID_SLOT_TYPES = {"photo", "text", "cta", "icon", "infographic"}
KEBAB = re.compile(r"^[a-z][a-z0-9-]*$")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        fail(f"missing required keys: {sorted(missing)}")
    if not KEBAB.match(data["id"]):
        fail(f"id must be kebab-case lowercase: {data['id']!r}")
    if data["category"] not in VALID_CATEGORIES:
        fail(f"invalid category: {data['category']!r}")
    if not isinstance(data["use_cases"], list) or not data["use_cases"]:
        fail("use_cases must be a non-empty list")
    for uc in data["use_cases"]:
        if uc not in VALID_USE_CASES:
            fail(f"invalid use_case: {uc!r}")
    if not isinstance(data["slots"], list):
        fail("slots must be a list (may be empty)")
    for i, slot in enumerate(data["slots"]):
        if not isinstance(slot, dict):
            fail(f"slot #{i} must be a mapping")
        if "type" not in slot or "name" not in slot:
            fail(f"slot #{i} missing type or name")
        if slot["type"] not in VALID_SLOT_TYPES:
            fail(f"slot #{i} invalid type: {slot['type']!r}")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-meta.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
```

- [ ] **Step 5: Запустить — должно пройти**

```bash
bats tests/phase-pra/test-validate-meta.bats
```
Ожидаемо: 4/4 PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/block-library-management/scripts/validate-meta.py tests/phase-pra/test-validate-meta.bats tests/phase-pra/fixtures/meta-*.yaml
git commit -m "feat(block-library): validate-meta.py + bats tests"
```

---

### Task 6: prototype.yaml validator

**Files:**
- Create: `skills/prototype-import/SKILL.md`
- Create: `skills/prototype-import/scripts/validate-prototype.py`
- Create: `tests/phase-pra/test-validate-prototype.bats`
- Create: `tests/phase-pra/fixtures/prototype-valid.yaml`
- Create: `tests/phase-pra/fixtures/prototype-missing-blocks.yaml`

- [ ] **Step 1: Fixtures**

`tests/phase-pra/fixtures/prototype-valid.yaml`:
```yaml
project:
  slug: example
  niche: services
  source_file: prototype.pdf
blocks:
  - position: 1
    type: hero
    headline: "Ремонт квартир под ключ в Москве"
    subhead: "Срок 30 дней, договор, гарантия 3 года"
    cta:
      text: "Рассчитать стоимость"
      action: scroll-to-quiz
    slots:
      - {type: photo, name: hero-bg, hint: "интерьер до/после"}
    mobile_notes: ""
  - position: 2
    type: features
    headline: "Почему мы"
    items:
      - {title: "Договор", text: "Фиксированная смета", icon_slot: "document"}
    mobile_notes: ""
```

`tests/phase-pra/fixtures/prototype-missing-blocks.yaml`:
```yaml
project:
  slug: x
  niche: services
  source_file: prototype.pdf
```

- [ ] **Step 2: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/prototype-import/scripts/validate-prototype.py"
}

@test "accepts valid prototype" {
  run python3 "$VALIDATOR" "$FIXTURES/prototype-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects prototype without blocks key" {
  run python3 "$VALIDATOR" "$FIXTURES/prototype-missing-blocks.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"blocks"* ]]
}

@test "rejects prototype with invalid niche" {
  cat > "$BATS_TMPDIR/bad-niche.yaml" <<EOF
project:
  slug: x
  niche: blogging
  source_file: x.pdf
blocks: []
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/bad-niche.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"niche"* ]]
}

@test "rejects prototype block missing position" {
  cat > "$BATS_TMPDIR/no-pos.yaml" <<EOF
project:
  slug: x
  niche: services
  source_file: x.pdf
blocks:
  - type: hero
    headline: "X"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/no-pos.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"position"* ]]
}
```

- [ ] **Step 3: validate-prototype.py**

```python
#!/usr/bin/env python3
"""Validate <project>/07_ПРОТОТИП/prototype.yaml schema."""
import sys
import yaml
from pathlib import Path

VALID_NICHES = {"services", "b2c", "local"}
VALID_BLOCK_TYPES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    if "project" not in data:
        fail("missing 'project' section")
    proj = data["project"]
    for k in ("slug", "niche", "source_file"):
        if k not in proj:
            fail(f"project.{k} required")
    if proj["niche"] not in VALID_NICHES:
        fail(f"invalid niche: {proj['niche']!r}")
    if "blocks" not in data:
        fail("missing 'blocks' section")
    if not isinstance(data["blocks"], list):
        fail("blocks must be a list")
    seen_positions = set()
    for i, block in enumerate(data["blocks"]):
        if not isinstance(block, dict):
            fail(f"block #{i} must be a mapping")
        if "position" not in block:
            fail(f"block #{i} missing position")
        if block["position"] in seen_positions:
            fail(f"duplicate position {block['position']}")
        seen_positions.add(block["position"])
        if "type" not in block:
            fail(f"block #{i} missing type")
        if block["type"] not in VALID_BLOCK_TYPES:
            fail(f"block #{i} invalid type: {block['type']!r}")
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-prototype.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
```

- [ ] **Step 4: Создать SKILL.md (минимум)**

`skills/prototype-import/SKILL.md`:
```markdown
---
name: prototype-import
description: Import user-provided prototype (PDF or MD) at stage 07 — parse, normalize to prototype.md (human) and prototype.yaml (machine). Used by /landing-prototype command and prototype-importer agent.
---

# prototype-import

Импорт пользовательского прототипа.

## Сценарий

1. Пользователь кладёт `prototype.pdf` или `prototype.md` в `<project>/07_ПРОТОТИП/source/`.
2. `/landing-prototype` запускает агента `prototype-importer`.
3. Агент использует скрипты:
   - `scripts/extract-pdf-text.py <input.pdf>` — извлечь текст (с OCR fallback через `anthropic-skills:pdf`)
   - `scripts/md-to-yaml.py <prototype.md>` — конвертировать структурированный MD в YAML
   - `scripts/validate-prototype.py <prototype.yaml>` — проверить схему
4. Пишет `prototype.md` + `prototype.yaml` + `import-log.md`.

## Schema

Полная schema — `scripts/validate-prototype.py`. Кратко:
- `project`: slug, niche (services|b2c|local), source_file
- `blocks[]`: position (unique int), type (hero|features|...), headline, subhead, cta, slots, items, mobile_notes
```

- [ ] **Step 5: Запустить тесты — должны пройти**

```bash
bats tests/phase-pra/test-validate-prototype.bats
```

- [ ] **Step 6: Commit**

```bash
git add skills/prototype-import/ tests/phase-pra/test-validate-prototype.bats tests/phase-pra/fixtures/prototype-*.yaml
git commit -m "feat(prototype-import): scaffold skill + validate-prototype.py + tests"
```

---

### Task 7: selections.yaml validator

**Files:**
- Create: `skills/block-composition/SKILL.md`
- Create: `skills/block-composition/scripts/validate-selections.py`
- Create: `tests/phase-pra/test-validate-selections.bats`
- Create: `tests/phase-pra/fixtures/selections-valid.yaml`
- Create: `tests/phase-pra/fixtures/selections-missing-confirm.yaml`

- [ ] **Step 1: Fixtures**

`tests/phase-pra/fixtures/selections-valid.yaml`:
```yaml
project_slug: example
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
  - block_position: 2
    chosen_variant: ru-features-02-bento-grid
confirmed_at: "2026-05-12T14:23:00Z"
```

`tests/phase-pra/fixtures/selections-missing-confirm.yaml`:
```yaml
project_slug: example
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
```

- [ ] **Step 2: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  VALIDATOR="$ROOT/skills/block-composition/scripts/validate-selections.py"
}

@test "accepts valid selections" {
  run python3 "$VALIDATOR" "$FIXTURES/selections-valid.yaml"
  [ "$status" -eq 0 ]
}

@test "rejects selections missing confirmed_at" {
  run python3 "$VALIDATOR" "$FIXTURES/selections-missing-confirm.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"confirmed_at"* ]]
}

@test "rejects selections with duplicate block_position" {
  cat > "$BATS_TMPDIR/dup.yaml" <<EOF
project_slug: example
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
  - block_position: 1
    chosen_variant: ru-hero-02-b2c-expert
confirmed_at: "2026-05-12T14:23:00Z"
EOF
  run python3 "$VALIDATOR" "$BATS_TMPDIR/dup.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate"* ]]
}
```

- [ ] **Step 3: validate-selections.py**

```python
#!/usr/bin/env python3
"""Validate <project>/07a_WIREFRAME/selections.yaml."""
import re
import sys
import yaml
from pathlib import Path

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path: str) -> None:
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict):
        fail("top-level must be a mapping")
    for k in ("project_slug", "selections", "confirmed_at"):
        if k not in data:
            fail(f"missing {k}")
    if not ISO_RE.match(str(data["confirmed_at"])):
        fail(f"confirmed_at must be ISO-8601: {data['confirmed_at']!r}")
    if not isinstance(data["selections"], list) or not data["selections"]:
        fail("selections must be a non-empty list")
    seen = set()
    for i, sel in enumerate(data["selections"]):
        if "block_position" not in sel or "chosen_variant" not in sel:
            fail(f"selection #{i}: needs block_position and chosen_variant")
        if sel["block_position"] in seen:
            fail(f"duplicate block_position: {sel['block_position']}")
        seen.add(sel["block_position"])
    print("OK")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-selections.py <path>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
```

- [ ] **Step 4: block-composition SKILL.md (минимум)**

`skills/block-composition/SKILL.md`:
```markdown
---
name: block-composition
description: Stage 07b — compose chosen blocks with design-tokens injected and prototype content substituted. Used by /landing-compose command and block-composer agent.
---

# block-composition

Сборка composed.html из утверждённых блоков и tokens.json.

## Scripts

- `scripts/validate-selections.py` — проверить `selections.yaml`
- `scripts/inject-tokens.py` — заменить CSS-переменные в template.html на значения из tokens.json
- `scripts/inject-content.py` — подставить тексты/заголовки/CTA из prototype.yaml
- `scripts/compose-blocks.py` — собрать composed.html (desktop) + composed-mobile.html

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `<project>/07a_WIREFRAME/selections.yaml`
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json`
- `block-library/` (общая)

## Outputs

- `<project>/07b_COMPOSED/composed.html`
- `<project>/07b_COMPOSED/composed-mobile.html`
- `<project>/07b_COMPOSED/block-injection-log.md`
```

- [ ] **Step 5: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-validate-selections.bats
```

- [ ] **Step 6: Commit**

```bash
git add skills/block-composition/ tests/phase-pra/test-validate-selections.bats tests/phase-pra/fixtures/selections-*.yaml
git commit -m "feat(block-composition): scaffold skill + validate-selections.py + tests"
```

---

## Phase 2 — Block scaffolder

### Task 8: scaffold-block.py — создание нового блока из шаблона

**Files:**
- Create: `skills/block-library-management/scripts/scaffold-block.py`
- Create: `tests/phase-pra/test-scaffold-block.bats`

- [ ] **Step 1: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCAFFOLDER="$ROOT/skills/block-library-management/scripts/scaffold-block.py"
  VALIDATOR="$ROOT/skills/block-library-management/scripts/validate-meta.py"
  CATALOG_VAL="$ROOT/skills/block-library-management/scripts/validate-catalog.py"
}

@test "scaffolds new block with all required files" {
  TMPDIR="$BATS_TMPDIR/lib-$$"
  mkdir -p "$TMPDIR/hero"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  run python3 "$SCAFFOLDER" \
      --id ru-hero-test-01 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  [ "$status" -eq 0 ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/SKILL.md" ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/assets/template.html" ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/assets/template-mobile.html" ]
  [ -f "$TMPDIR/hero/ru-hero-test-01/meta.yaml" ]
}

@test "scaffolded meta.yaml passes validator" {
  TMPDIR="$BATS_TMPDIR/lib-meta-$$"
  mkdir -p "$TMPDIR/hero"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  python3 "$SCAFFOLDER" \
      --id ru-hero-test-02 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  run python3 "$VALIDATOR" "$TMPDIR/hero/ru-hero-test-02/meta.yaml"
  [ "$status" -eq 0 ]
}

@test "scaffolded catalog.yaml passes validator" {
  TMPDIR="$BATS_TMPDIR/lib-cat-$$"
  mkdir -p "$TMPDIR/hero"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks: []
EOF
  python3 "$SCAFFOLDER" \
      --id ru-hero-test-03 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  run python3 "$CATALOG_VAL" "$TMPDIR/catalog.yaml"
  [ "$status" -eq 0 ]
}

@test "refuses to scaffold over existing block id" {
  TMPDIR="$BATS_TMPDIR/lib-dup-$$"
  mkdir -p "$TMPDIR/hero/ru-hero-test-04"
  cat > "$TMPDIR/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-test-04
    path: hero/ru-hero-test-04/
    category: hero
    use_cases: [services]
EOF
  run python3 "$SCAFFOLDER" \
      --id ru-hero-test-04 \
      --category hero \
      --library "$TMPDIR" \
      --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template"
  [ "$status" -ne 0 ]
  [[ "$output" == *"already exists"* ]]
}
```

- [ ] **Step 2: Запустить — fail**

- [ ] **Step 3: scaffold-block.py**

```python
#!/usr/bin/env python3
"""Scaffold a new block in block-library/ from the template-source dir.

Usage:
  scaffold-block.py --id <kebab-id> --category <cat> --library <path> --template-source <path>
"""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

VALID_CATEGORIES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
KEBAB = re.compile(r"^[a-z][a-z0-9-]*$")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--template-source", required=True)
    p.add_argument("--use-cases", default="services,b2c,local",
                   help="comma-separated; default all")
    args = p.parse_args()

    if not KEBAB.match(args.id):
        fail(f"id must be kebab-case: {args.id!r}")
    if args.category not in VALID_CATEGORIES:
        fail(f"invalid category: {args.category!r}")

    lib = Path(args.library)
    target = lib / args.category / args.id
    if target.exists():
        fail(f"block already exists: {target}")

    catalog_path = lib / "catalog.yaml"
    if not catalog_path.exists():
        fail(f"catalog.yaml not found in {lib}")
    catalog = yaml.safe_load(catalog_path.read_text())
    for b in catalog.get("blocks", []):
        if b["id"] == args.id:
            fail(f"id already in catalog: {args.id}")

    src = Path(args.template_source)
    if not src.exists():
        fail(f"template source not found: {src}")

    shutil.copytree(src, target)

    # Fill in meta.yaml
    meta_path = target / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text())
    meta["id"] = args.id
    meta["category"] = args.category
    meta["use_cases"] = [u.strip() for u in args.use_cases.split(",")]
    meta["created"] = date.today().isoformat()
    meta_path.write_text(yaml.dump(meta, sort_keys=False, allow_unicode=True))

    # Replace {{block_id}} placeholders in templates
    for html_name in ("template.html", "template-mobile.html"):
        html_path = target / "assets" / html_name
        text = html_path.read_text()
        text = text.replace("{{block_id}}", args.id)
        html_path.write_text(text)

    # Update SKILL.md placeholder
    skill_path = target / "SKILL.md"
    text = skill_path.read_text()
    text = text.replace("<block-id>", args.id)
    skill_path.write_text(text)

    # Update catalog
    catalog.setdefault("blocks", []).append({
        "id": args.id,
        "path": f"{args.category}/{args.id}/",
        "category": args.category,
        "use_cases": meta["use_cases"],
    })
    catalog["updated"] = date.today().isoformat()
    catalog_path.write_text(yaml.dump(catalog, sort_keys=False, allow_unicode=True))

    print(f"OK: scaffolded {target}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-scaffold-block.bats
```

- [ ] **Step 5: Commit**

```bash
git add skills/block-library-management/scripts/scaffold-block.py tests/phase-pra/test-scaffold-block.bats
git commit -m "feat(block-library): scaffold-block.py + bats tests"
```

---

## Phase 3 — Seed all 17 blocks

### Task 9: Создать 17 seed-блоков через scaffolder + наполнить контентом

**Files** (создаются скаффолдером, потом редактируются):
- 17 папок `block-library/<category>/<id>/` со всеми файлами (SKILL.md, assets/template.html, assets/template-mobile.html, meta.yaml)

**Block roster** (zero-padding double digits для сортировки):

| # | id | category | use_cases |
|---|---|---|---|
| 1 | `ru-hero-01-services-calc` | hero | services |
| 2 | `ru-hero-02-b2c-expert` | hero | b2c |
| 3 | `ru-hero-03-local-interior` | hero | local |
| 4 | `ru-features-01-3col-icons` | features | services, b2c, local |
| 5 | `ru-features-02-bento-grid` | features | services, b2c, local |
| 6 | `ru-testimonials-01-video-circles` | social-proof | services, b2c, local |
| 7 | `ru-testimonials-02-text-photo` | social-proof | services, b2c, local |
| 8 | `ru-process-01-4steps-icons` | process | services, local |
| 9 | `ru-pricing-01-rub-from` | pricing | services, b2c, local |
| 10 | `ru-trust-01-guarantees-docs` | trust | services, local |
| 11 | `ru-cta-01-callback-tg-max` | cta | services, b2c, local |
| 12 | `ru-faq-01-accordion` | faq | services, b2c, local |
| Q1 | `ru-quiz-01-step-card` | quiz | services, b2c, local |
| Q2 | `ru-quiz-02-progress-top` | quiz | services, b2c, local |
| Q3 | `ru-quiz-03-intermediate` | quiz | services, b2c, local |
| Q4 | `ru-quiz-04-lead-form` | quiz | services, b2c, local |
| Q5 | `ru-quiz-05-thankyou` | quiz | services, b2c, local |

- [ ] **Step 1: Скаффолд все 17 блоков**

```bash
cd "$(git rev-parse --show-toplevel)"
ROOT="$(pwd)"

# Helper function — выполняется в bash
scaffold() {
  python3 "$ROOT/skills/block-library-management/scripts/scaffold-block.py" \
    --id "$1" --category "$2" \
    --library "$ROOT/block-library" \
    --template-source "$ROOT/vendor/opendesign-extracts/skill-block-template" \
    --use-cases "$3"
}

scaffold ru-hero-01-services-calc hero services
scaffold ru-hero-02-b2c-expert hero b2c
scaffold ru-hero-03-local-interior hero local
scaffold ru-features-01-3col-icons features services,b2c,local
scaffold ru-features-02-bento-grid features services,b2c,local
scaffold ru-testimonials-01-video-circles social-proof services,b2c,local
scaffold ru-testimonials-02-text-photo social-proof services,b2c,local
scaffold ru-process-01-4steps-icons process services,local
scaffold ru-pricing-01-rub-from pricing services,b2c,local
scaffold ru-trust-01-guarantees-docs trust services,local
scaffold ru-cta-01-callback-tg-max cta services,b2c,local
scaffold ru-faq-01-accordion faq services,b2c,local
scaffold ru-quiz-01-step-card quiz services,b2c,local
scaffold ru-quiz-02-progress-top quiz services,b2c,local
scaffold ru-quiz-03-intermediate quiz services,b2c,local
scaffold ru-quiz-04-lead-form quiz services,b2c,local
scaffold ru-quiz-05-thankyou quiz services,b2c,local
```

- [ ] **Step 2: Заполнить полным контентом `ru-hero-01-services-calc` (полный образец)**

`block-library/hero/ru-hero-01-services-calc/SKILL.md`:
```markdown
---
name: ru-hero-01-services-calc
description: RU hero для услуг с фоновым фото объекта, оффером слева и кнопкой "Рассчитать стоимость". Контраст 7:1, sticky CTA, плашка "от X ₽".
---

# ru-hero-01-services-calc

## Когда применять

Hero-блок для проектов в нише **услуг** (ремонт, строительство, медицина, юристы), где главный конверсионный сценарий — расчёт стоимости через калькулятор/квиз.

## Slots

- `hero-bg` (photo, 16:9 desktop / 9:16 mobile) — фото объекта / процесса работы. Обязательный.
- `headline` (text, ≤60 char) — название услуги + локация. Обязательный.
- `subhead` (text, ≤120 char) — три ключевых преимущества через запятую (срок, договор, гарантия).
- `price-tag` (text, ~12 char) — плашка "от X ₽". Опциональный.
- `primary-cta` (cta, default "Рассчитать стоимость") — обязательная.

## Conversion notes

- CTA контраст к фону ≥ 7:1.
- Плашка "от X ₽" в правом верхнем углу desktop, под заголовком на mobile.
- На mobile фото перемещается под заголовок (не на фон).

## Mobile considerations

`template-mobile.html` использует stack-layout: photo сверху, текст снизу, CTA полной шириной.
```

`block-library/hero/ru-hero-01-services-calc/assets/template.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>ru-hero-01-services-calc — desktop</title>
<style>
  :root {
    --color-bg: #fff;
    --color-fg: #111;
    --color-accent: #333;
    --font-display: system-ui, sans-serif;
    --font-body: system-ui, sans-serif;
    --spacing-lg: 32px;
  }
  body { margin: 0; font-family: var(--font-body); background: var(--color-bg); color: var(--color-fg); }
  .hero { display: grid; grid-template-columns: 1fr 1fr; min-height: 600px; }
  .hero-text { padding: var(--spacing-lg); display: flex; flex-direction: column; justify-content: center; }
  .hero-photo { background: #ddd; position: relative; }
  .hero-photo .slot-label { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
  .headline { font-family: var(--font-display); font-size: 42px; line-height: 1.1; margin: 0 0 16px; }
  .subhead { font-size: 18px; color: #444; margin: 0 0 24px; }
  .price-tag { position: absolute; top: 24px; right: 24px; background: rgba(255,255,255,0.95); padding: 8px 16px; border-radius: 4px; font-weight: 600; }
  .cta { display: inline-block; padding: 16px 32px; background: var(--color-accent); color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; }
</style>
</head>
<body>
  <section class="hero" data-block-id="ru-hero-01-services-calc">
    <div class="hero-text">
      <h1 class="headline" data-slot="headline">[HEADLINE: услуга + локация]</h1>
      <p class="subhead" data-slot="subhead">[SUBHEAD: срок, договор, гарантия]</p>
      <a class="cta" data-slot="primary-cta" href="#quiz">[CTA: Рассчитать стоимость]</a>
    </div>
    <div class="hero-photo" data-slot="hero-bg">
      <div class="slot-label">photo · 16:9 · hero-bg</div>
      <div class="price-tag" data-slot="price-tag">[от X ₽]</div>
    </div>
  </section>
</body>
</html>
```

`block-library/hero/ru-hero-01-services-calc/assets/template-mobile.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>ru-hero-01-services-calc — mobile</title>
<style>
  :root {
    --color-bg: #fff; --color-fg: #111; --color-accent: #333;
    --font-display: system-ui, sans-serif;
    --font-body: system-ui, sans-serif;
  }
  body { margin: 0; font-family: var(--font-body); background: var(--color-bg); color: var(--color-fg); width: 375px; }
  .hero-photo { aspect-ratio: 9/16; background: #ddd; position: relative; }
  .hero-photo .slot-label { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 11px; color: #666; }
  .hero-text { padding: 20px; }
  .headline { font-family: var(--font-display); font-size: 28px; line-height: 1.15; margin: 0 0 12px; }
  .subhead { font-size: 15px; color: #444; margin: 0 0 16px; }
  .price-tag { display: inline-block; background: #f4f4f4; padding: 6px 12px; border-radius: 4px; font-weight: 600; margin-bottom: 16px; }
  .cta { display: block; padding: 14px; background: var(--color-accent); color: #fff; text-align: center; text-decoration: none; border-radius: 6px; font-weight: 600; }
</style>
</head>
<body>
  <section class="hero" data-block-id="ru-hero-01-services-calc">
    <div class="hero-photo" data-slot="hero-bg">
      <div class="slot-label">photo · 9:16 · hero-bg</div>
    </div>
    <div class="hero-text">
      <h1 class="headline" data-slot="headline">[HEADLINE]</h1>
      <p class="subhead" data-slot="subhead">[SUBHEAD]</p>
      <div class="price-tag" data-slot="price-tag">[от X ₽]</div>
      <a class="cta" data-slot="primary-cta" href="#quiz">[Рассчитать стоимость]</a>
    </div>
  </section>
</body>
</html>
```

`block-library/hero/ru-hero-01-services-calc/meta.yaml`:
```yaml
id: ru-hero-01-services-calc
category: hero
ru_market: true
use_cases: [services]
description: "RU hero для услуг: фоновое фото объекта, оффер слева, кнопка 'Рассчитать стоимость', плашка 'от X ₽'"
slots:
  - {type: photo, name: hero-bg, ratio: "16:9", mobile_ratio: "9:16", required: true}
  - {type: text, name: headline, max_chars: 60, required: true}
  - {type: text, name: subhead, max_chars: 120, required: false}
  - {type: text, name: price-tag, max_chars: 12, required: false}
  - {type: cta, name: primary-cta, default_text: "Рассчитать стоимость", required: true}
conversion_notes: "CTA контраст 7:1. Плашка 'от X ₽' в углу desktop, под subhead на mobile. Sticky CTA после скролла за hero."
source: manual
source_attribution: ""
created: 2026-05-12
```

- [ ] **Step 3: Заполнить полным контентом `ru-quiz-04-lead-form` (второй полный образец, потому что quiz — особый случай с TG/Max/без WhatsApp)**

`block-library/quiz/ru-quiz-04-lead-form/SKILL.md`:
```markdown
---
name: ru-quiz-04-lead-form
description: Финальный экран квиза — собирает контакты. БЕЗ WhatsApp (запрещён в РФ). С Telegram + Max Messenger + телефоном.
---

# ru-quiz-04-lead-form

## Когда применять

Последний шаг квиза после всех вопросов — точка сбора лида.

## Slots

- `headline` (text, ≤80 char) — призыв оставить контакт. Обязательный.
- `subhead` (text, ≤140 char) — что получит пользователь.
- `phone-input` — поле телефона. Обязательное.
- `name-input` — поле имени. Опциональное.
- `channel-choice` — radio-кнопки: Telegram / Max / звонок. Обязательное.
- `submit-cta` (cta, default "Получить расчёт") — обязательная.
- `agreement-text` (text) — согласие на обработку ПД.

## Conversion notes

- **WhatsApp убран** (запрещён в РФ с 2026).
- Max Messenger обязателен (растущая аудитория в РФ).
- Согласие на ПД — checkbox по умолчанию НЕ отмечен (152-ФЗ требует opt-in).

## Mobile considerations

Поля во всю ширину, channel-choice вертикальный stack.
```

`block-library/quiz/ru-quiz-04-lead-form/assets/template.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>ru-quiz-04-lead-form — desktop</title>
<style>
  :root {
    --color-bg: #fff; --color-fg: #111; --color-accent: #333;
    --color-border: #ccc; --spacing-md: 16px;
    --font-body: system-ui, sans-serif;
  }
  body { margin: 0; font-family: var(--font-body); background: var(--color-bg); color: var(--color-fg); }
  .lead-form { max-width: 520px; margin: 80px auto; padding: 32px; border: 1px solid var(--color-border); border-radius: 12px; }
  .headline { font-size: 28px; line-height: 1.2; margin: 0 0 12px; }
  .subhead { color: #555; margin: 0 0 24px; }
  .field { margin-bottom: 16px; }
  .field input[type=text], .field input[type=tel] { width: 100%; padding: 12px; border: 1px solid var(--color-border); border-radius: 6px; font-size: 16px; box-sizing: border-box; }
  .channel-choice { display: flex; gap: 12px; margin-bottom: 16px; }
  .channel-choice label { flex: 1; padding: 12px; border: 1px solid var(--color-border); border-radius: 6px; cursor: pointer; text-align: center; }
  .channel-choice input { display: none; }
  .channel-choice input:checked + span { font-weight: 600; }
  .agreement { display: flex; gap: 8px; font-size: 13px; color: #666; margin-bottom: 16px; }
  .cta { width: 100%; padding: 16px; background: var(--color-accent); color: #fff; border: none; border-radius: 6px; font-weight: 600; font-size: 16px; cursor: pointer; }
</style>
</head>
<body>
  <section class="lead-form" data-block-id="ru-quiz-04-lead-form">
    <h2 class="headline" data-slot="headline">[HEADLINE: оставь контакт]</h2>
    <p class="subhead" data-slot="subhead">[SUBHEAD: что получит пользователь]</p>
    <div class="field"><input type="text" placeholder="Имя" data-slot="name-input"></div>
    <div class="field"><input type="tel" placeholder="+7 ___ ___ __ __" data-slot="phone-input" required></div>
    <fieldset class="channel-choice" data-slot="channel-choice">
      <label><input type="radio" name="ch" value="tg" checked><span>Telegram</span></label>
      <label><input type="radio" name="ch" value="max"><span>Max</span></label>
      <label><input type="radio" name="ch" value="phone"><span>Звонок</span></label>
    </fieldset>
    <label class="agreement"><input type="checkbox" required><span data-slot="agreement-text">Согласен на обработку персональных данных (152-ФЗ)</span></label>
    <button class="cta" data-slot="submit-cta">[Получить расчёт]</button>
  </section>
</body>
</html>
```

`block-library/quiz/ru-quiz-04-lead-form/assets/template-mobile.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>ru-quiz-04-lead-form — mobile</title>
<style>
  :root { --color-bg:#fff; --color-fg:#111; --color-accent:#333; --color-border:#ccc; }
  body { margin: 0; font-family: system-ui, sans-serif; background: var(--color-bg); color: var(--color-fg); width: 375px; }
  .lead-form { padding: 20px; }
  .headline { font-size: 22px; line-height: 1.2; margin: 0 0 8px; }
  .subhead { color: #555; font-size: 14px; margin: 0 0 16px; }
  .field { margin-bottom: 12px; }
  .field input { width: 100%; padding: 12px; border: 1px solid var(--color-border); border-radius: 6px; font-size: 16px; box-sizing: border-box; }
  .channel-choice { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
  .channel-choice label { padding: 12px; border: 1px solid var(--color-border); border-radius: 6px; text-align: center; }
  .channel-choice input { display: none; }
  .agreement { display: flex; gap: 8px; font-size: 12px; color: #666; margin-bottom: 16px; }
  .cta { width: 100%; padding: 14px; background: var(--color-accent); color: #fff; border: none; border-radius: 6px; font-weight: 600; }
</style>
</head>
<body>
  <section class="lead-form" data-block-id="ru-quiz-04-lead-form">
    <h2 class="headline">[HEADLINE]</h2>
    <p class="subhead">[SUBHEAD]</p>
    <div class="field"><input type="text" placeholder="Имя"></div>
    <div class="field"><input type="tel" placeholder="+7 ___ ___ __ __"></div>
    <fieldset class="channel-choice">
      <label><input type="radio" name="ch" value="tg" checked>Telegram</label>
      <label><input type="radio" name="ch" value="max">Max</label>
      <label><input type="radio" name="ch" value="phone">Звонок</label>
    </fieldset>
    <label class="agreement"><input type="checkbox" required> Согласен на обработку ПД (152-ФЗ)</label>
    <button class="cta">[Получить расчёт]</button>
  </section>
</body>
</html>
```

`block-library/quiz/ru-quiz-04-lead-form/meta.yaml`:
```yaml
id: ru-quiz-04-lead-form
category: quiz
ru_market: true
use_cases: [services, b2c, local]
description: "Финальный экран квиза. Telegram + Max + звонок. БЕЗ WhatsApp (запрещён в РФ). Согласие на ПД."
slots:
  - {type: text, name: headline, max_chars: 80, required: true}
  - {type: text, name: subhead, max_chars: 140, required: false}
  - {type: text, name: name-input, max_chars: 50, required: false}
  - {type: text, name: phone-input, max_chars: 20, required: true}
  - {type: text, name: channel-choice, required: true}
  - {type: cta, name: submit-cta, default_text: "Получить расчёт", required: true}
  - {type: text, name: agreement-text, max_chars: 200, required: true}
conversion_notes: "WhatsApp убран — запрещён в РФ. Max Messenger обязателен. 152-ФЗ checkbox НЕ pre-checked."
source: manual
source_attribution: ""
created: 2026-05-12
```

- [ ] **Step 4: Заполнить оставшиеся 15 блоков**

Для каждого блока из таблицы roster (кроме `ru-hero-01-services-calc` и `ru-quiz-04-lead-form` — уже сделаны):

Используй scaffolded шаблоны как стартовую точку, замени контент по краткой спецификации:

| Block ID | Краткая spec |
|---|---|
| `ru-hero-02-b2c-expert` | Левая колонка: фото эксперта в круге + имя + регалии (например "Психолог, 15 лет практики"). Правая: оффер, sub, CTA "Подобрать программу". |
| `ru-hero-03-local-interior` | Full-width фото интерьера. Поверх: оверлей с заголовком + CTA "Записаться". Плашка часов работы. |
| `ru-features-01-3col-icons` | 3 колонки. Каждая: иконка (slot) + заголовок (≤30 char) + текст (≤80 char). |
| `ru-features-02-bento-grid` | Bento grid 2x2: одна большая ячейка (фото), три мелкие (текст+иконка). |
| `ru-testimonials-01-video-circles` | Карусель круглых видео-кружков (Reels-style). Каждый кружок: photo placeholder + имя клиента + текст отзыва. |
| `ru-testimonials-02-text-photo` | Карточки 2x2: фото клиента слева, цитата справа, имя+регалии снизу. |
| `ru-process-01-4steps-icons` | 4 шага с цифрами 1-2-3-4, иконка + заголовок + описание под каждой. Mobile — вертикальный stack. |
| `ru-pricing-01-rub-from` | 3 тарифа (Базовый / Стандарт / Премиум). Заголовок + "от X ₽" большим + список 5 пунктов галочками + CTA. |
| `ru-trust-01-guarantees-docs` | 4 плашки: договор / лицензия / гарантия / возврат. Иконка + заголовок + 1 строка. |
| `ru-cta-01-callback-tg-max` | Центрированный CTA-блок: заголовок + 3 кнопки рядом: "Telegram" / "Max" / "Перезвоните мне". |
| `ru-faq-01-accordion` | Аккордеон 6 вопросов. Только CSS (через `<details>` тег — нативно работает). |
| `ru-quiz-01-step-card` | Карточка с вопросом сверху + 4 кнопки-варианта + комментарий "зачем спрашиваем" мелким шрифтом снизу. |
| `ru-quiz-02-progress-top` | Sticky-bar сверху: "Вопрос N из M" + progress bar. Используется поверх других quiz-блоков. |
| `ru-quiz-03-intermediate` | Полноэкранный блок: большой emoji 💪 + текст "Осталось 2 шага" + кнопка "Продолжить". |
| `ru-quiz-05-thankyou` | Полноэкранный финал: галочка + "Спасибо! Свяжемся в TG/Max через 5 минут" + кнопка "На главную". |

**Правила для каждого блока:**
1. Стартовое содержимое уже создано scaffolder'ом.
2. Перепиши `assets/template.html` под spec.
3. Перепиши `assets/template-mobile.html` под mobile-вариант той же spec.
4. Обнови `meta.yaml`: description, slots (соответствующие реальному template), conversion_notes.
5. Перепиши `SKILL.md`: краткое описание + slots + conversion notes.
6. Каждый template.html обязан содержать CSS-переменные в `:root`: `--color-bg`, `--color-fg`, `--color-accent`, `--font-display`, `--font-body`, `--spacing-md`, `--spacing-lg`, `--color-border`. Block-composer полагается на эти имена при инжекте токенов.
7. Каждый `data-slot="<name>"` атрибут на elements должен соответствовать `slots[].name` в meta.yaml.

- [ ] **Step 5: Валидация всех 17 блоков**

```bash
ROOT="$(git rev-parse --show-toplevel)"
python3 "$ROOT/skills/block-library-management/scripts/validate-catalog.py" "$ROOT/block-library/catalog.yaml"
for d in "$ROOT"/block-library/*/*/meta.yaml; do
  python3 "$ROOT/skills/block-library-management/scripts/validate-meta.py" "$d" || exit 1
done
echo "All 17 blocks valid."
```

- [ ] **Step 6: Создать bats тест на seed-блоки**

`tests/phase-pra/test-seed-blocks.bats`:
```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  LIB="$ROOT/block-library"
  CATVAL="$ROOT/skills/block-library-management/scripts/validate-catalog.py"
  METAVAL="$ROOT/skills/block-library-management/scripts/validate-meta.py"
}

@test "catalog.yaml is valid" {
  run python3 "$CATVAL" "$LIB/catalog.yaml"
  [ "$status" -eq 0 ]
}

@test "all 17 seed blocks present and meta valid" {
  expected_count=17
  count=0
  for d in "$LIB"/*/*/meta.yaml; do
    run python3 "$METAVAL" "$d"
    [ "$status" -eq 0 ]
    count=$((count + 1))
  done
  [ "$count" -eq "$expected_count" ]
}

@test "every block has desktop and mobile template" {
  for d in "$LIB"/*/*/; do
    [ -f "$d/assets/template.html" ]
    [ -f "$d/assets/template-mobile.html" ]
  done
}

@test "every block template references at least one CSS var --color-accent" {
  for d in "$LIB"/*/*/; do
    grep -q -- "--color-accent" "$d/assets/template.html"
  done
}

@test "no quiz block contains WhatsApp reference" {
  ! grep -ril "whatsapp\|вотсап" "$LIB/quiz/"
}
```

- [ ] **Step 7: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-seed-blocks.bats
```

- [ ] **Step 8: Commit (один коммит на всю seed-партию)**

```bash
git add block-library/ tests/phase-pra/test-seed-blocks.bats
git commit -m "feat(block-library): seed 17 RU blocks (12 base + 5 quiz)"
```

---

## Phase 4 — prototype-import implementation

### Task 10: extract-pdf-text.py (с OCR fallback)

**Files:**
- Create: `skills/prototype-import/scripts/extract-pdf-text.py`
- Create: `tests/phase-pra/test-extract-pdf-text.bats`
- Create: `tests/phase-pra/fixtures/prototype-sample-text.pdf` (генерируем в тесте)

- [ ] **Step 1: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  EXTRACT="$ROOT/skills/prototype-import/scripts/extract-pdf-text.py"

  # Generate a simple text PDF for testing
  PYGEN=$(cat <<'PY'
from pypdf import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import sys, io

out = sys.argv[1]
c = canvas.Canvas(out, pagesize=A4)
c.drawString(100, 750, "Hero block")
c.drawString(100, 720, "Headline: Test landing")
c.drawString(100, 690, "CTA: Get started")
c.save()
PY
)
  if python3 -c "import reportlab" 2>/dev/null; then
    python3 -c "$PYGEN" "$BATS_TMPDIR/sample.pdf"
  else
    # Fallback: skip generation, use stub
    skip_reason="reportlab not installed; skipping pdf generation tests"
  fi
}

@test "extract text from a simple text PDF" {
  if [ ! -f "$BATS_TMPDIR/sample.pdf" ]; then skip "reportlab not installed"; fi
  run python3 "$EXTRACT" "$BATS_TMPDIR/sample.pdf"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Hero block"* ]]
  [[ "$output" == *"Test landing"* ]]
}

@test "non-existent file exits non-zero" {
  run python3 "$EXTRACT" "$BATS_TMPDIR/does-not-exist.pdf"
  [ "$status" -ne 0 ]
}

@test "exit non-zero if file is empty" {
  touch "$BATS_TMPDIR/empty.pdf"
  run python3 "$EXTRACT" "$BATS_TMPDIR/empty.pdf"
  [ "$status" -ne 0 ]
}
```

- [ ] **Step 2: extract-pdf-text.py**

```python
#!/usr/bin/env python3
"""Extract text from a PDF prototype file.

Strategy:
1. Try text extraction via pypdf.
2. If empty (likely scanned PDF), suggest OCR via anthropic-skills:pdf.

Outputs raw text to stdout. Exit 0 on success, non-zero on failure.

Usage: extract-pdf-text.py <input.pdf>
"""
import sys
from pathlib import Path


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        fail(f"file not found: {path}")
    if path.stat().st_size == 0:
        fail("file is empty")

    try:
        from pypdf import PdfReader
    except ImportError:
        fail("pypdf is required. Install: pip install pypdf")

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        fail(f"cannot open PDF: {e}")

    text_parts: list[str] = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            text_parts.append("")

    full = "\n".join(text_parts).strip()
    if not full:
        # Empty extraction → recommend OCR
        print(
            "ERROR: No text extracted (likely scanned PDF). "
            "Use anthropic-skills:pdf for OCR fallback.",
            file=sys.stderr,
        )
        sys.exit(2)

    print(full)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract-pdf-text.py <path>", file=sys.stderr)
        sys.exit(3)
    main(sys.argv[1])
```

- [ ] **Step 3: Запустить тесты**

```bash
bats tests/phase-pra/test-extract-pdf-text.bats
```

Если `pypdf` или `reportlab` не установлены — добавь их в `requirements.txt`:

```bash
echo "pypdf>=4.0.0" >> requirements.txt
echo "reportlab>=4.0.0" >> requirements.txt
pip install -r requirements.txt
```

Затем перезапусти тесты — должны пройти.

- [ ] **Step 4: Commit**

```bash
git add skills/prototype-import/scripts/extract-pdf-text.py tests/phase-pra/test-extract-pdf-text.bats requirements.txt
git commit -m "feat(prototype-import): extract-pdf-text.py with text-first strategy + OCR fallback hint"
```

---

### Task 11: md-to-yaml.py — структурированный MD → prototype.yaml

**Files:**
- Create: `skills/prototype-import/scripts/md-to-yaml.py`
- Create: `tests/phase-pra/test-md-to-yaml.bats`
- Create: `tests/phase-pra/fixtures/prototype-sample.md`

Формат MD, который мы парсим:

```markdown
# Project: example
# Niche: services

## Block 1: hero
- headline: Ремонт квартир под ключ в Москве
- subhead: Срок 30 дней, договор, гарантия 3 года
- cta: Рассчитать стоимость
- slot photo hero-bg: интерьер до/после

## Block 2: features
- headline: Почему мы
- item: Договор | Фиксированная смета | icon: document
- item: Гарантия 3 года | Всё в договоре | icon: shield
```

- [ ] **Step 1: Fixture**

`tests/phase-pra/fixtures/prototype-sample.md`:
```markdown
# Project: example
# Niche: services

## Block 1: hero
- headline: Ремонт квартир под ключ в Москве
- subhead: Срок 30 дней, договор, гарантия 3 года
- cta: Рассчитать стоимость
- slot photo hero-bg: интерьер до/после

## Block 2: features
- headline: Почему мы
- item: Договор | Фиксированная смета | icon: document
- item: Гарантия 3 года | Всё в договоре | icon: shield
```

- [ ] **Step 2: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  CONVERTER="$ROOT/skills/prototype-import/scripts/md-to-yaml.py"
  VALIDATOR="$ROOT/skills/prototype-import/scripts/validate-prototype.py"
}

@test "converts sample MD to valid YAML" {
  run python3 "$CONVERTER" "$FIXTURES/prototype-sample.md" "$BATS_TMPDIR/out.yaml"
  [ "$status" -eq 0 ]
  [ -f "$BATS_TMPDIR/out.yaml" ]
  run python3 "$VALIDATOR" "$BATS_TMPDIR/out.yaml"
  [ "$status" -eq 0 ]
}

@test "yaml preserves block order and headlines" {
  python3 "$CONVERTER" "$FIXTURES/prototype-sample.md" "$BATS_TMPDIR/out.yaml"
  run python3 -c "
import yaml, sys
d = yaml.safe_load(open('$BATS_TMPDIR/out.yaml'))
assert d['blocks'][0]['type'] == 'hero', d['blocks'][0]
assert d['blocks'][0]['headline'].startswith('Ремонт'), d['blocks'][0]
assert d['blocks'][1]['type'] == 'features', d['blocks'][1]
assert len(d['blocks'][1]['items']) == 2, d['blocks'][1]
print('OK')
"
  [ "$status" -eq 0 ]
}

@test "exits non-zero on malformed MD missing Project header" {
  cat > "$BATS_TMPDIR/bad.md" <<EOF
## Block 1: hero
- headline: x
EOF
  run python3 "$CONVERTER" "$BATS_TMPDIR/bad.md" "$BATS_TMPDIR/out2.yaml"
  [ "$status" -ne 0 ]
  [[ "$output" == *"Project"* ]]
}
```

- [ ] **Step 3: md-to-yaml.py**

```python
#!/usr/bin/env python3
"""Convert a structured prototype.md to prototype.yaml.

Expected MD format:
    # Project: <slug>
    # Niche: <services|b2c|local>

    ## Block N: <type>
    - headline: ...
    - subhead: ...
    - cta: ...
    - slot <type> <name>: <hint>
    - item: <title> | <text> | icon: <icon-name>

Usage: md-to-yaml.py <input.md> <output.yaml>
"""
import re
import sys
import yaml
from pathlib import Path

BLOCK_HEADER = re.compile(r"^##\s+Block\s+(\d+):\s+(\w[\w-]*)\s*$")
PROJECT_LINE = re.compile(r"^#\s+Project:\s*(\S+)\s*$")
NICHE_LINE = re.compile(r"^#\s+Niche:\s*(\w+)\s*$")
SLOT_LINE = re.compile(r"^-\s*slot\s+(\w+)\s+([\w-]+):\s*(.*)$")
KV_LINE = re.compile(r"^-\s*([\w-]+):\s*(.+)$")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(in_path: str, out_path: str) -> None:
    lines = Path(in_path).read_text().splitlines()

    project: dict = {}
    blocks: list = []
    current: dict | None = None

    for raw in lines:
        line = raw.rstrip()
        if not line:
            continue

        m = PROJECT_LINE.match(line)
        if m:
            project["slug"] = m.group(1)
            continue

        m = NICHE_LINE.match(line)
        if m:
            project["niche"] = m.group(1)
            continue

        m = BLOCK_HEADER.match(line)
        if m:
            if current is not None:
                blocks.append(current)
            current = {
                "position": int(m.group(1)),
                "type": m.group(2),
                "slots": [],
            }
            continue

        if current is None:
            continue  # ignore stray content

        m = SLOT_LINE.match(line)
        if m:
            current["slots"].append({
                "type": m.group(1),
                "name": m.group(2),
                "hint": m.group(3).strip(),
            })
            continue

        m = KV_LINE.match(line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            if key == "item":
                # "<title> | <text> | icon: <icon>"
                parts = [p.strip() for p in val.split("|")]
                item = {"title": parts[0] if parts else ""}
                if len(parts) > 1:
                    item["text"] = parts[1]
                if len(parts) > 2 and parts[2].startswith("icon:"):
                    item["icon_slot"] = parts[2].split(":", 1)[1].strip()
                current.setdefault("items", []).append(item)
            elif key == "cta":
                current["cta"] = {"text": val, "action": ""}
            else:
                current[key] = val
            continue

    if current is not None:
        blocks.append(current)

    if "slug" not in project or "niche" not in project:
        fail("missing # Project: or # Niche: header")
    if not blocks:
        fail("no '## Block N: <type>' sections found")

    project["source_file"] = Path(in_path).name
    out = {"project": project, "blocks": blocks}
    Path(out_path).write_text(yaml.dump(out, sort_keys=False, allow_unicode=True))
    print(f"OK: wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: md-to-yaml.py <input.md> <output.yaml>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
```

- [ ] **Step 4: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-md-to-yaml.bats
```

- [ ] **Step 5: Commit**

```bash
git add skills/prototype-import/scripts/md-to-yaml.py tests/phase-pra/test-md-to-yaml.bats tests/phase-pra/fixtures/prototype-sample.md
git commit -m "feat(prototype-import): md-to-yaml.py converter + tests"
```

---

### Task 12: prototype-importer agent

**Files:**
- Create: `agents/prototype-importer.md`

- [ ] **Step 1: Создать agent**

```markdown
---
name: prototype-importer
description: Use during stage 07 (Прототип) to import a user-provided prototype.pdf or prototype.md from source/, normalize to prototype.md (human) and prototype.yaml (machine), and write import-log.md. Asks clarifying questions on ambiguity instead of guessing.
---

# prototype-importer

## Mission

Импорт пользовательского прототипа из `<project>/07_ПРОТОТИП/source/` → нормализованные артефакты `prototype.md` + `prototype.yaml` + `import-log.md`.

## Inputs

- `<project>/07_ПРОТОТИП/source/prototype.pdf` или `source/prototype.md` (один из них должен существовать)

## Outputs

- `<project>/07_ПРОТОТИП/prototype.md` — human-readable normalized
- `<project>/07_ПРОТОТИП/prototype.yaml` — machine-readable (валидируется validate-prototype.py)
- `<project>/07_ПРОТОТИП/import-log.md` — что понял агент, какие вопросы задавал

## Workflow

1. Найди исходник:
   ```bash
   ls "$PROJECT/07_ПРОТОТИП/source/"
   ```
2. Если `prototype.pdf`:
   - Попробуй `python3 skills/prototype-import/scripts/extract-pdf-text.py source/prototype.pdf > /tmp/pdf-text.txt`
   - Если exit code 2 (нет текста — сканированный PDF) — используй `anthropic-skills:pdf` через Skill tool для OCR
   - Если exit code != 0 в принципе — STOP, сообщи пользователю
3. Если `prototype.md`:
   - Прочитай напрямую
4. Из извлечённого текста собери структурированный `prototype.md` по формату:
   ```
   # Project: <slug>
   # Niche: <services|b2c|local>

   ## Block 1: <type>
   - headline: ...
   - cta: ...
   - slot <type> <name>: <hint>
   ```
5. **Если что-то непонятно — спроси у пользователя:**
   - какая ниша (services / b2c / local)?
   - block #N не определился — это hero, features, или что?
   - нашёл "Калькулятор стоимости" — это quiz или pricing блок?

   Ответы запиши в `import-log.md`.
6. Запусти конвертер: `python3 skills/prototype-import/scripts/md-to-yaml.py prototype.md prototype.yaml`
7. Запусти валидатор: `python3 skills/prototype-import/scripts/validate-prototype.py prototype.yaml`
8. Если валидация упала — исправь `prototype.md` и повтори.

## CRITICAL CONSTRAINT — no inventing

Если в прототипе нет нужной информации (например, не указан CTA) — НЕ ВЫДУМЫВАЙ.
Запиши `cta: ""` и в `import-log.md` отметь: "CTA не найден, использован пустой".
Это даст пользователю явный сигнал доуточнить.

## HARD GATE

После записи артефактов сообщи пользователю:
> ✅ Прототип импортирован.
> - `prototype.md` — проверь правильность извлечения, при необходимости отредактируй.
> - После правок MD запусти заново `md-to-yaml.py` (или просто `/landing-prototype` ещё раз).
> - Когда будешь готов — запускай `/landing-wireframe`.

## Tools

Read, Write, Edit, Bash, Glob, Skill (для anthropic-skills:pdf OCR fallback).
```

- [ ] **Step 2: bats тест что файл существует и parsable**

```bash
cat > tests/phase-pra/test-agents-exist.bats <<'EOF'
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
}

@test "prototype-importer agent file exists" {
  [ -f "$ROOT/agents/prototype-importer.md" ]
}

@test "prototype-importer has required frontmatter" {
  run head -5 "$ROOT/agents/prototype-importer.md"
  [[ "$output" == *"name: prototype-importer"* ]]
  [[ "$output" == *"description:"* ]]
}
EOF

bats tests/phase-pra/test-agents-exist.bats
```

Ожидаемо: PASS.

- [ ] **Step 3: Commit**

```bash
git add agents/prototype-importer.md tests/phase-pra/test-agents-exist.bats
git commit -m "feat(agents): add prototype-importer agent"
```

---

### Task 13: /landing-prototype command

**Files:**
- Create: `commands/landing-prototype.md`

- [ ] **Step 1: Создать command**

```markdown
---
description: Stage 07 — import user-provided prototype (PDF or MD) from <project>/07_ПРОТОТИП/source/, normalize to prototype.{md,yaml}, write import-log.md.
---

# /landing-prototype

Запускает этап **07_ПРОТОТИП** — импорт пользовательского прототипа.

## Что делает

1. Проверяет, что текущая папка — проект-лендинг (есть `00_БРИФ/brief.md` или `.landing-state.yaml`).
2. Проверяет, что в `07_ПРОТОТИП/source/` существует `prototype.pdf` или `prototype.md`.
3. Передаёт работу агенту `prototype-importer`.
4. После завершения работы агента запускает валидатор:
   ```bash
   python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
   ```
5. Сообщает summary + предлагает запустить `/landing-wireframe`.

## Артефакты после выполнения

- `07_ПРОТОТИП/prototype.md`
- `07_ПРОТОТИП/prototype.yaml`
- `07_ПРОТОТИП/import-log.md`

## Условия запуска

- Текущая папка — проект-лендинг
- В `07_ПРОТОТИП/source/` лежит `prototype.pdf` или `prototype.md`

## После одобрения

Запускай `/landing-wireframe`.

## NOTE (PR-A scope)

Эта команда **не** интегрирована со `scripts/gate-check.sh` и `.landing-state.yaml`.
Интеграция в орекстратор и enforce порядка этапов — задача PR-D.
До PR-D — команды вызываются вручную, пользователь сам решает что делать дальше.
```

- [ ] **Step 2: bats тест что файл существует**

```bash
cat >> tests/phase-pra/test-agents-exist.bats <<'EOF'

@test "landing-prototype command file exists" {
  [ -f "$ROOT/commands/landing-prototype.md" ]
}

@test "landing-prototype command has description frontmatter" {
  run head -3 "$ROOT/commands/landing-prototype.md"
  [[ "$output" == *"description:"* ]]
}
EOF

bats tests/phase-pra/test-agents-exist.bats
```

- [ ] **Step 3: Commit**

```bash
git add commands/landing-prototype.md tests/phase-pra/test-agents-exist.bats
git commit -m "feat(commands): /landing-prototype"
```

---

## Phase 5 — ux-composer & wireframe-rendering

### Task 14: match-candidates.py — подбор кандидатов из block-library

**Files:**
- Create: `skills/wireframe-rendering/SKILL.md`
- Create: `skills/wireframe-rendering/scripts/match-candidates.py`
- Create: `tests/phase-pra/test-match-candidates.bats`

Стратегия matching:
1. Берём блок прототипа `type` (например `hero`).
2. Из catalog.yaml выбираем все блоки этой category.
3. Фильтруем по `use_cases` пересечение с project.niche.
4. Возвращаем top-N (по умолчанию 3) — сортировка: совпадение всех use_cases > совпадение одного > общие блоки.

- [ ] **Step 1: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  MATCHER="$ROOT/skills/wireframe-rendering/scripts/match-candidates.py"

  # Build temp library with 3 hero blocks
  TMPLIB="$BATS_TMPDIR/lib-$$"
  mkdir -p "$TMPLIB/hero"
  cat > "$TMPLIB/catalog.yaml" <<EOF
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-01-services-calc
    path: hero/ru-hero-01-services-calc/
    category: hero
    use_cases: [services]
  - id: ru-hero-02-b2c-expert
    path: hero/ru-hero-02-b2c-expert/
    category: hero
    use_cases: [b2c]
  - id: ru-hero-03-local-interior
    path: hero/ru-hero-03-local-interior/
    category: hero
    use_cases: [local]
  - id: ru-features-01-3col-icons
    path: features/ru-features-01-3col-icons/
    category: features
    use_cases: [services, b2c, local]
EOF
}

@test "matches services hero" {
  run python3 "$MATCHER" --library "$TMPLIB" --type hero --niche services --top 3
  [ "$status" -eq 0 ]
  [[ "$output" == *"ru-hero-01-services-calc"* ]]
}

@test "matches features for any niche" {
  run python3 "$MATCHER" --library "$TMPLIB" --type features --niche services --top 3
  [ "$status" -eq 0 ]
  [[ "$output" == *"ru-features-01-3col-icons"* ]]
}

@test "returns nothing when no category match" {
  run python3 "$MATCHER" --library "$TMPLIB" --type pricing --niche services --top 3
  [ "$status" -eq 0 ]
  [ -z "$(echo "$output" | grep -v '^\[\]$')" ] || [ "$output" == "[]" ]
}

@test "respects --top limit" {
  run python3 "$MATCHER" --library "$TMPLIB" --type hero --niche services --top 1
  [ "$status" -eq 0 ]
  count=$(echo "$output" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
  [ "$count" -eq 1 ]
}
```

- [ ] **Step 2: match-candidates.py**

```python
#!/usr/bin/env python3
"""Match block-library candidates for a given prototype block.

Selects blocks from catalog where category matches and use_cases overlap
with project niche. Returns top-N sorted by use_cases overlap descending.

Usage: match-candidates.py --library <path> --type <hero|...> --niche <services|b2c|local> [--top 3]

Output: JSON array of block ids to stdout.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--library", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--niche", required=True)
    p.add_argument("--top", type=int, default=3)
    args = p.parse_args()

    cat_path = Path(args.library) / "catalog.yaml"
    if not cat_path.exists():
        print(f"ERROR: no catalog.yaml in {args.library}", file=sys.stderr)
        sys.exit(1)
    catalog = yaml.safe_load(cat_path.read_text())

    scored: list[tuple[int, str]] = []
    for block in catalog.get("blocks", []):
        if block["category"] != args.type:
            continue
        if args.niche in block["use_cases"]:
            # score: more specific (single use_case match) sometimes preferred,
            # but we use "explicit niche match" first, "generic all-three" second
            score = 10 if len(block["use_cases"]) == 1 else 5
            scored.append((score, block["id"]))

    scored.sort(key=lambda x: -x[0])
    top_ids = [b for _, b in scored[: args.top]]
    print(json.dumps(top_ids))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: SKILL.md для wireframe-rendering**

```markdown
---
name: wireframe-rendering
description: Stage 07a — render interactive wireframe.html (desktop+mobile per block with CSS-only radio toggles between 2-3 candidates) from prototype.yaml + block-library. Used by /landing-wireframe and ux-composer agent.
---

# wireframe-rendering

## Что делает

Рендерит `<project>/07a_WIREFRAME/wireframe.html` — интерактивный preview, где для каждого блока прототипа показано 2-3 варианта композиции из `block-library/`. Переключение между вариантами — CSS-only (`:checked` selector), без сборки/JS-фреймворков.

## Scripts

- `scripts/match-candidates.py` — выбрать кандидатов из catalog
- `scripts/render-wireframe.py` — собрать wireframe.html из шаблона + кандидатов
- `scripts/serve-preview.sh` — опциональный `python -m http.server` для случаев, когда `file://` ломает iframe sandbox

## Templates

- `templates/wireframe-shell.html` — оболочка с radio-кнопками и CSS

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `block-library/catalog.yaml`
- `block-library/<category>/<block-id>/assets/template.html|template-mobile.html`

## Outputs

- `<project>/07a_WIREFRAME/wireframe.html`
- `<project>/07a_WIREFRAME/candidates.yaml`
```

- [ ] **Step 4: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-match-candidates.bats
```

- [ ] **Step 5: Commit**

```bash
git add skills/wireframe-rendering/ tests/phase-pra/test-match-candidates.bats
git commit -m "feat(wireframe-rendering): match-candidates.py + skill scaffold"
```

---

### Task 15: render-wireframe.py — сборка interactive HTML

**Files:**
- Create: `skills/wireframe-rendering/scripts/render-wireframe.py`
- Create: `skills/wireframe-rendering/templates/wireframe-shell.html`
- Create: `tests/phase-pra/test-render-wireframe.bats`

- [ ] **Step 1: Шаблон оболочки**

`skills/wireframe-rendering/templates/wireframe-shell.html`:
```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Wireframe — {{project_slug}}</title>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; background: #f0f0f0; }
  .block-slot { margin: 24px; background: #fff; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .variant-picker { border: none; padding: 0; margin: 0 0 16px; }
  .variant-picker legend { font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #333; }
  .variant-picker label { display: inline-block; padding: 6px 12px; margin-right: 8px; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; }
  .variants-stage { display: block; }
  .variant { display: none; gap: 24px; flex-wrap: wrap; }
  .device { border: 1px solid #ddd; background: #fff; }
  .device.desktop { width: 1280px; max-width: 100%; }
  .device.mobile { width: 375px; }
  .device-label { font-size: 11px; color: #888; padding: 4px 8px; background: #fafafa; }
  .device iframe { width: 100%; border: none; display: block; }

  /* Generated radio:checked selectors injected below */
  {{checked_rules}}

  .confirm-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #111; color: #fff; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
  .confirm-bar button { padding: 12px 24px; background: #fff; color: #111; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
</style>
</head>
<body>
<h1 style="padding: 24px;">Wireframe — {{project_slug}}</h1>
<p style="padding: 0 24px; color: #666;">Выбери вариант композиции для каждого блока с помощью radio-кнопок. Когда закончишь — нажми «Confirm selections» внизу.</p>

{{blocks_html}}

<div class="confirm-bar">
  <span>Выбери варианты для всех блоков, затем подтверди.</span>
  <button onclick="confirmSelections()">Confirm selections</button>
</div>

<script>
/* Minimal inline JS — read radio selections, build selections.yaml,
   prompt download. ~30 lines, no external deps. */
function confirmSelections() {
  const radios = document.querySelectorAll('input[type=radio]:checked');
  const sel = [];
  radios.forEach(r => {
    sel.push({
      block_position: parseInt(r.getAttribute('data-position'), 10),
      chosen_variant: r.value,
    });
  });
  sel.sort((a, b) => a.block_position - b.block_position);
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  let yaml = `project_slug: {{project_slug}}\nselections:\n`;
  sel.forEach(s => {
    yaml += `  - block_position: ${s.block_position}\n    chosen_variant: ${s.chosen_variant}\n`;
  });
  yaml += `confirmed_at: "${now}"\n`;
  const blob = new Blob([yaml], {type: 'text/yaml'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'selections.yaml';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
</script>
</body>
</html>
```

- [ ] **Step 2: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  RENDERER="$ROOT/skills/wireframe-rendering/scripts/render-wireframe.py"

  PROJECT="$BATS_TMPDIR/proj-$$"
  mkdir -p "$PROJECT/07_ПРОТОТИП" "$PROJECT/07a_WIREFRAME"
  cat > "$PROJECT/07_ПРОТОТИП/prototype.yaml" <<EOF
project:
  slug: example
  niche: services
  source_file: prototype.pdf
blocks:
  - position: 1
    type: hero
    headline: "Test"
    slots: []
EOF
}

@test "renders wireframe.html and candidates.yaml" {
  run python3 "$RENDERER" \
      --project "$PROJECT" \
      --library "$ROOT/block-library" \
      --template "$ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
  [ "$status" -eq 0 ]
  [ -f "$PROJECT/07a_WIREFRAME/wireframe.html" ]
  [ -f "$PROJECT/07a_WIREFRAME/candidates.yaml" ]
}

@test "wireframe.html contains radio inputs" {
  python3 "$RENDERER" \
      --project "$PROJECT" \
      --library "$ROOT/block-library" \
      --template "$ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
  run grep -c 'type="radio"' "$PROJECT/07a_WIREFRAME/wireframe.html"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "wireframe.html contains :checked CSS selector" {
  python3 "$RENDERER" \
      --project "$PROJECT" \
      --library "$ROOT/block-library" \
      --template "$ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
  run grep -c ':checked' "$PROJECT/07a_WIREFRAME/wireframe.html"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}
```

- [ ] **Step 3: render-wireframe.py**

```python
#!/usr/bin/env python3
"""Render <project>/07a_WIREFRAME/wireframe.html from prototype.yaml + block-library.

Strategy:
  For each block in prototype:
    1. Call match-candidates logic inline to get top-3 candidate block ids.
    2. Read each candidate's template.html and template-mobile.html.
    3. Embed both into an inline iframe via srcdoc (sandboxed).
    4. Emit radio-buttons with data-position=<block.position>, value=<candidate_id>.
    5. Emit CSS :checked selectors so only the chosen variant is visible.

Outputs candidates.yaml alongside.
"""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

import yaml

CHECKED_TPL = (
    "#{rid}:checked ~ .variants-stage [data-variant=\"{rid}\"] {{ display: flex; }}"
)


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--top", type=int, default=3)
    args = p.parse_args()

    project_dir = Path(args.project)
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if not proto_path.exists():
        fail(f"no prototype.yaml at {proto_path}")
    proto = yaml.safe_load(proto_path.read_text())
    niche = proto["project"]["niche"]
    slug = proto["project"]["slug"]

    matcher_script = (
        Path(__file__).parent / "match-candidates.py"
    )

    blocks_html_parts: list[str] = []
    checked_rules: list[str] = []
    candidates_log: dict = {"project_slug": slug, "blocks": []}

    for block in proto["blocks"]:
        position = block["position"]
        btype = block["type"]
        res = subprocess.run(
            [
                "python3", str(matcher_script),
                "--library", args.library,
                "--type", btype,
                "--niche", niche,
                "--top", str(args.top),
            ],
            capture_output=True, text=True, check=True,
        )
        candidate_ids = json.loads(res.stdout)
        if not candidate_ids:
            candidates_log["blocks"].append({
                "block_position": position,
                "block_type": btype,
                "candidates": [],
                "warning": f"no candidates for {btype} / {niche}",
            })
            blocks_html_parts.append(
                f'<section class="block-slot"><strong>Block {position} ({btype})</strong>: '
                f'no candidates found for niche {niche}.</section>'
            )
            continue

        candidates_log["blocks"].append({
            "block_position": position,
            "block_type": btype,
            "candidates": candidate_ids,
        })

        radios = []
        variants = []
        for i, cid in enumerate(candidate_ids):
            cat = _category_for(args.library, cid)
            block_dir = Path(args.library) / cat / cid
            tmpl_d = (block_dir / "assets" / "template.html").read_text()
            tmpl_m = (block_dir / "assets" / "template-mobile.html").read_text()

            rid = f"b{position}-v{i}"
            checked = "checked" if i == 0 else ""
            radios.append(
                f'<input type="radio" name="b{position}" id="{rid}" '
                f'value="{cid}" data-position="{position}" {checked}>'
                f'<label for="{rid}">{html.escape(cid)}</label>'
            )
            variants.append(
                f'<div class="variant" data-variant="{rid}">'
                f'<div class="device desktop"><div class="device-label">Desktop · {cid}</div>'
                f'<iframe sandbox srcdoc="{html.escape(tmpl_d, quote=True)}"></iframe></div>'
                f'<div class="device mobile"><div class="device-label">Mobile · {cid}</div>'
                f'<iframe sandbox srcdoc="{html.escape(tmpl_m, quote=True)}"></iframe></div>'
                f'</div>'
            )
            checked_rules.append(CHECKED_TPL.format(rid=rid))

        section = (
            f'<section class="block-slot" data-block-position="{position}">'
            f'<fieldset class="variant-picker">'
            f'<legend>Block {position} — {btype} — выбери композицию:</legend>'
            f'{"".join(radios)}'
            f'</fieldset>'
            f'<div class="variants-stage">{"".join(variants)}</div>'
            f'</section>'
        )
        blocks_html_parts.append(section)

    shell = Path(args.template).read_text()
    out = (
        shell.replace("{{project_slug}}", slug)
        .replace("{{blocks_html}}", "\n".join(blocks_html_parts))
        .replace("{{checked_rules}}", "\n".join(checked_rules))
    )
    out_html = project_dir / "07a_WIREFRAME" / "wireframe.html"
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(out)

    (project_dir / "07a_WIREFRAME" / "candidates.yaml").write_text(
        yaml.dump(candidates_log, sort_keys=False, allow_unicode=True)
    )

    print(f"OK: rendered {out_html}")


def _category_for(library: str, block_id: str) -> str:
    cat = yaml.safe_load((Path(library) / "catalog.yaml").read_text())
    for b in cat.get("blocks", []):
        if b["id"] == block_id:
            return b["category"]
    raise SystemExit(f"ERROR: block {block_id} not in catalog")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: serve-preview.sh helper**

`skills/wireframe-rendering/scripts/serve-preview.sh`:
```bash
#!/usr/bin/env bash
# Optional helper — serves wireframe.html over http://localhost:8000
# Useful when file:// breaks iframe sandboxing.
#
# Usage: serve-preview.sh <project>/07a_WIREFRAME/

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <project>/07a_WIREFRAME/" >&2
  exit 2
fi

DIR="$1"
PORT="${PORT:-8000}"

if [ ! -f "$DIR/wireframe.html" ]; then
  echo "ERROR: $DIR/wireframe.html not found" >&2
  exit 1
fi

echo "Serving $DIR at http://localhost:$PORT/wireframe.html"
echo "Press Ctrl+C to stop."
cd "$DIR"
exec python3 -m http.server "$PORT"
```

```bash
chmod +x skills/wireframe-rendering/scripts/serve-preview.sh
```

- [ ] **Step 5: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-render-wireframe.bats
```

- [ ] **Step 6: Commit**

```bash
git add skills/wireframe-rendering/scripts/render-wireframe.py skills/wireframe-rendering/scripts/serve-preview.sh skills/wireframe-rendering/templates/wireframe-shell.html tests/phase-pra/test-render-wireframe.bats
git commit -m "feat(wireframe-rendering): render-wireframe.py + interactive shell template + serve helper"
```

---

### Task 16: ux-composer agent + /landing-wireframe command

**Files:**
- Create: `agents/ux-composer.md`
- Create: `commands/landing-wireframe.md`

- [ ] **Step 1: agents/ux-composer.md**

```markdown
---
name: ux-composer
description: Use during stage 07a (UX Wireframe) to compose an interactive wireframe.html from prototype.yaml + block-library. NEVER invents blocks — strictly selects from library via pre-flight injection. Asks "need new block?" instead of fabricating.
---

# ux-composer

## Mission

Между Design.md и кодом — собрать `wireframe.html` с 2-3 вариантами композиции на каждый блок прототипа. Пользователь выбирает variant radio-кнопками, скачивает `selections.yaml`.

## CRITICAL — pre-flight injection contract

Перед началом работы агент инжектит в свой контекст:

1. `<project>/07_ПРОТОТИП/prototype.yaml` — целиком
2. `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — целиком (для будущей compose-фазы)
3. `<project>/04_БРЕНД/brand-kit.md` — целиком
4. `block-library/catalog.yaml` — список доступных блоков
5. `ui-ux-pro-max/data/landing.csv` — релевантные RU-паттерны

**Правило железное:** агент НЕ ПРИДУМЫВАЕТ блоки. Если для блока прототипа ни один блок из library не подходит — агент возвращает `needs_new_block: true` с reasoning. Это сигнал пользователю либо переписать прототип, либо добавить новый блок в library через `scaffold-block.py`.

## Workflow

1. Проверь, что `07_ПРОТОТИП/prototype.yaml` существует и валиден:
   ```bash
   python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
   ```
2. Запусти рендер:
   ```bash
   python3 skills/wireframe-rendering/scripts/render-wireframe.py \
       --project "$PWD" \
       --library "$LANDING_SYSTEM_ROOT/block-library" \
       --template "$LANDING_SYSTEM_ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"
   ```
3. Прочитай `07a_WIREFRAME/candidates.yaml`. Если хоть в одном блоке `candidates: []` — сообщи пользователю:
   > Для блока N (`<type>`) нет подходящих вариантов. Нужен новый блок? Команда:
   > `python3 skills/block-library-management/scripts/scaffold-block.py --id <new-id> --category <type>`
4. Сообщи путь к `wireframe.html` и попроси:
   > Открой `07a_WIREFRAME/wireframe.html` двойным кликом. Выбери варианты radio-кнопками. Нажми «Confirm selections» внизу — скачается `selections.yaml`. Положи его в `07a_WIREFRAME/selections.yaml`.

## HARD GATE

Пока `07a_WIREFRAME/selections.yaml` не существует — следующие этапы недоступны.

## Tools

Read, Write, Bash.
```

- [ ] **Step 2: commands/landing-wireframe.md**

```markdown
---
description: Stage 07a — render interactive wireframe.html with 2-3 block-library candidates per prototype block. User picks variants via radio buttons.
---

# /landing-wireframe

Запускает этап **07a_WIREFRAME**.

## Что делает

1. Проверяет наличие `07_ПРОТОТИП/prototype.yaml`.
2. Передаёт работу агенту `ux-composer`.
3. После рендера сообщает путь к `07a_WIREFRAME/wireframe.html` и инструкцию по выбору вариантов.

## Артефакты

- `07a_WIREFRAME/wireframe.html` — интерактивный preview
- `07a_WIREFRAME/candidates.yaml` — список кандидатов на блок

После выбора пользователем:
- `07a_WIREFRAME/selections.yaml` (создаётся пользователем через кнопку Confirm)

## Условия запуска

- `07_ПРОТОТИП/prototype.yaml` существует и валиден

## После одобрения

Запускай `/landing-compose`.

## NOTE (PR-A scope)

Не интегрировано в `landing-orchestrator` и `.landing-state.yaml` — задача PR-D.
```

- [ ] **Step 3: bats тест**

```bash
cat >> tests/phase-pra/test-agents-exist.bats <<'EOF'

@test "ux-composer agent file exists" {
  [ -f "$ROOT/agents/ux-composer.md" ]
}

@test "landing-wireframe command file exists" {
  [ -f "$ROOT/commands/landing-wireframe.md" ]
}
EOF

bats tests/phase-pra/test-agents-exist.bats
```

- [ ] **Step 4: Commit**

```bash
git add agents/ux-composer.md commands/landing-wireframe.md tests/phase-pra/test-agents-exist.bats
git commit -m "feat(agents,commands): ux-composer + /landing-wireframe"
```

---

## Phase 6 — block-composition

### Task 17: inject-tokens.py — подстановка CSS-переменных из tokens.json

**Files:**
- Create: `skills/block-composition/scripts/inject-tokens.py`
- Create: `tests/phase-pra/test-inject-tokens.bats`
- Create: `tests/phase-pra/fixtures/tokens-sample.json`

- [ ] **Step 1: Fixture**

`tests/phase-pra/fixtures/tokens-sample.json`:
```json
{
  "color": {
    "bg": "#fafafa",
    "fg": "#1a1a1a",
    "accent": "#ff4d4d",
    "border": "#e0e0e0"
  },
  "font": {
    "display": "Manrope, sans-serif",
    "body": "Inter, sans-serif"
  },
  "spacing": {
    "md": "16px",
    "lg": "48px"
  }
}
```

- [ ] **Step 2: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-pra/fixtures"
  INJECTOR="$ROOT/skills/block-composition/scripts/inject-tokens.py"
}

@test "replaces --color-accent in template" {
  cat > "$BATS_TMPDIR/in.html" <<EOF
<html><head><style>
:root { --color-bg: #fff; --color-fg: #000; --color-accent: #333; }
</style></head><body></body></html>
EOF
  run python3 "$INJECTOR" "$BATS_TMPDIR/in.html" "$FIXTURES/tokens-sample.json" "$BATS_TMPDIR/out.html"
  [ "$status" -eq 0 ]
  grep -q -- "--color-accent: #ff4d4d" "$BATS_TMPDIR/out.html"
}

@test "replaces --font-display in template" {
  cat > "$BATS_TMPDIR/in2.html" <<EOF
<html><head><style>
:root { --font-display: system-ui, sans-serif; --font-body: serif; }
</style></head><body></body></html>
EOF
  python3 "$INJECTOR" "$BATS_TMPDIR/in2.html" "$FIXTURES/tokens-sample.json" "$BATS_TMPDIR/out2.html"
  grep -q -- "--font-display: Manrope, sans-serif" "$BATS_TMPDIR/out2.html"
}

@test "preserves CSS vars not present in tokens.json" {
  cat > "$BATS_TMPDIR/in3.html" <<EOF
<html><head><style>
:root { --color-unknown: pink; --color-accent: #333; }
</style></head><body></body></html>
EOF
  python3 "$INJECTOR" "$BATS_TMPDIR/in3.html" "$FIXTURES/tokens-sample.json" "$BATS_TMPDIR/out3.html"
  grep -q -- "--color-unknown: pink" "$BATS_TMPDIR/out3.html"
  grep -q -- "--color-accent: #ff4d4d" "$BATS_TMPDIR/out3.html"
}
```

- [ ] **Step 3: inject-tokens.py**

```python
#!/usr/bin/env python3
"""Replace CSS custom properties in a template.html with values from tokens.json.

Mapping convention:
  tokens.json key "color.accent" → CSS var --color-accent
  tokens.json key "font.display" → CSS var --font-display
  tokens.json key "spacing.lg"   → CSS var --spacing-lg

CSS vars NOT covered in tokens.json are preserved verbatim.

Usage: inject-tokens.py <template.html> <tokens.json> <output.html>
"""
import json
import re
import sys
from pathlib import Path


def flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in d.items():
        key = f"{prefix}-{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = str(v)
    return out


def main(in_html: str, tokens_path: str, out_html: str) -> None:
    html_text = Path(in_html).read_text()
    tokens = json.loads(Path(tokens_path).read_text())
    flat = flatten(tokens)
    # flat keys like "color-accent", "font-display"

    def repl(match: re.Match) -> str:
        name = match.group(1)  # without --
        if name in flat:
            return f"--{name}: {flat[name]};"
        return match.group(0)

    pattern = re.compile(r"--([\w-]+):\s*[^;]+;")
    new_text = pattern.sub(repl, html_text)
    Path(out_html).write_text(new_text)
    print(f"OK: wrote {out_html}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: inject-tokens.py <in.html> <tokens.json> <out.html>", file=sys.stderr)
        sys.exit(2)
    main(*sys.argv[1:])
```

- [ ] **Step 4: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-inject-tokens.bats
```

- [ ] **Step 5: Commit**

```bash
git add skills/block-composition/scripts/inject-tokens.py tests/phase-pra/test-inject-tokens.bats tests/phase-pra/fixtures/tokens-sample.json
git commit -m "feat(block-composition): inject-tokens.py + tests"
```

---

### Task 18: inject-content.py — подстановка текстов из prototype.yaml

**Files:**
- Create: `skills/block-composition/scripts/inject-content.py`
- Create: `tests/phase-pra/test-inject-content.bats`

Стратегия: для каждого элемента в шаблоне с `data-slot="<name>"`:
- Если в prototype.yaml для этого блока есть поле с матчингом имени слота — заменить inner text.
- Иначе — заменить на видимый placeholder `[SLOT: <name>]`.

- [ ] **Step 1: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  INJECTOR="$ROOT/skills/block-composition/scripts/inject-content.py"
}

@test "substitutes headline into data-slot=headline element" {
  cat > "$BATS_TMPDIR/tmpl.html" <<EOF
<h1 data-slot="headline">[HEADLINE]</h1>
EOF
  cat > "$BATS_TMPDIR/proto.yaml" <<EOF
project: {slug: x, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    headline: "Test headline"
    slots: []
EOF
  run python3 "$INJECTOR" \
      --template "$BATS_TMPDIR/tmpl.html" \
      --prototype "$BATS_TMPDIR/proto.yaml" \
      --position 1 \
      --output "$BATS_TMPDIR/out.html"
  [ "$status" -eq 0 ]
  grep -q "Test headline" "$BATS_TMPDIR/out.html"
  ! grep -q "\[HEADLINE\]" "$BATS_TMPDIR/out.html"
}

@test "substitutes cta text" {
  cat > "$BATS_TMPDIR/tmpl2.html" <<EOF
<a data-slot="primary-cta">[CTA]</a>
EOF
  cat > "$BATS_TMPDIR/proto2.yaml" <<EOF
project: {slug: x, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    cta:
      text: "Buy now"
      action: ""
    slots: []
EOF
  python3 "$INJECTOR" --template "$BATS_TMPDIR/tmpl2.html" \
      --prototype "$BATS_TMPDIR/proto2.yaml" --position 1 --output "$BATS_TMPDIR/out2.html"
  grep -q "Buy now" "$BATS_TMPDIR/out2.html"
}

@test "leaves placeholder for missing slots" {
  cat > "$BATS_TMPDIR/tmpl3.html" <<EOF
<div data-slot="hero-bg"><span class="slot-label">photo</span></div>
EOF
  cat > "$BATS_TMPDIR/proto3.yaml" <<EOF
project: {slug: x, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    slots:
      - {type: photo, name: hero-bg, hint: "интерьер до/после"}
EOF
  python3 "$INJECTOR" --template "$BATS_TMPDIR/tmpl3.html" \
      --prototype "$BATS_TMPDIR/proto3.yaml" --position 1 --output "$BATS_TMPDIR/out3.html"
  grep -q "интерьер до/после" "$BATS_TMPDIR/out3.html"
}
```

- [ ] **Step 2: inject-content.py**

```python
#!/usr/bin/env python3
"""Inject prototype.yaml content into a template.html via data-slot attributes.

Rules:
  - Element with data-slot="headline" → replace inner content with block.headline
  - data-slot="subhead" → block.subhead
  - data-slot="primary-cta" or "submit-cta" or any cta-suffix → block.cta.text
  - data-slot="<photo-slot-name>" — render a placeholder block listing the
    slot hint from prototype's slots list.
  - Unknown slots → keep visible placeholder "[SLOT: <name>]"

Uses BeautifulSoup for safe HTML manipulation.

Usage:
  inject-content.py --template <html> --prototype <yaml> --position <int> --output <html>
"""
import argparse
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--position", type=int, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    proto = yaml.safe_load(Path(args.prototype).read_text())
    block = next(
        (b for b in proto["blocks"] if b["position"] == args.position),
        None,
    )
    if block is None:
        fail(f"no block with position {args.position} in prototype")

    soup = BeautifulSoup(Path(args.template).read_text(), "html.parser")
    photo_slots = {s["name"]: s for s in block.get("slots", []) if s["type"] == "photo"}

    for el in soup.select("[data-slot]"):
        slot_name = el["data-slot"]
        if slot_name == "headline" and "headline" in block:
            el.clear()
            el.append(NavigableString(block["headline"]))
        elif slot_name == "subhead" and "subhead" in block:
            el.clear()
            el.append(NavigableString(block["subhead"]))
        elif slot_name.endswith("-cta") and "cta" in block:
            el.clear()
            el.append(NavigableString(block["cta"].get("text", "")))
        elif slot_name in photo_slots:
            label_div = soup.new_tag("div", **{"class": "slot-placeholder"})
            label_div.append(NavigableString(
                f"[photo slot: {slot_name} — hint: {photo_slots[slot_name].get('hint', '')}]"
            ))
            el.clear()
            el.append(label_div)
        else:
            # Leave a clearly visible placeholder
            el.clear()
            el.append(NavigableString(f"[SLOT: {slot_name}]"))

    Path(args.output).write_text(str(soup))
    print(f"OK: wrote {args.output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Установить beautifulsoup4 если нет**

```bash
pip show beautifulsoup4 >/dev/null 2>&1 || echo "beautifulsoup4>=4.12.0" >> requirements.txt
pip install -r requirements.txt
```

- [ ] **Step 4: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-inject-content.bats
```

- [ ] **Step 5: Commit**

```bash
git add skills/block-composition/scripts/inject-content.py tests/phase-pra/test-inject-content.bats requirements.txt
git commit -m "feat(block-composition): inject-content.py + tests"
```

---

### Task 19: compose-blocks.py — финальная сборка composed.html

**Files:**
- Create: `skills/block-composition/scripts/compose-blocks.py`
- Create: `tests/phase-pra/test-compose-blocks.bats`

- [ ] **Step 1: bats тест**

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  COMPOSER="$ROOT/skills/block-composition/scripts/compose-blocks.py"

  PROJECT="$BATS_TMPDIR/proj-$$"
  mkdir -p "$PROJECT/07_ПРОТОТИП" "$PROJECT/07a_WIREFRAME" "$PROJECT/05_ДИЗАЙН-СИСТЕМА"

  cat > "$PROJECT/07_ПРОТОТИП/prototype.yaml" <<EOF
project: {slug: test, niche: services, source_file: x.pdf}
blocks:
  - position: 1
    type: hero
    headline: "Hello world"
    cta: {text: "Click", action: ""}
    slots: []
EOF

  cat > "$PROJECT/07a_WIREFRAME/selections.yaml" <<EOF
project_slug: test
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
confirmed_at: "2026-05-12T14:23:00Z"
EOF

  cat > "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json" <<EOF
{"color":{"bg":"#fff","fg":"#000","accent":"#0066cc"},"font":{"display":"sans","body":"sans"},"spacing":{"md":"16px","lg":"32px"}}
EOF
}

@test "produces composed.html and composed-mobile.html" {
  run python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  [ "$status" -eq 0 ]
  [ -f "$PROJECT/07b_COMPOSED/composed.html" ]
  [ -f "$PROJECT/07b_COMPOSED/composed-mobile.html" ]
}

@test "composed.html contains prototype headline" {
  python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  grep -q "Hello world" "$PROJECT/07b_COMPOSED/composed.html"
}

@test "composed.html contains accent color from tokens" {
  python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  grep -q "#0066cc" "$PROJECT/07b_COMPOSED/composed.html"
}

@test "block-injection-log.md is created" {
  python3 "$COMPOSER" --project "$PROJECT" --library "$ROOT/block-library"
  [ -f "$PROJECT/07b_COMPOSED/block-injection-log.md" ]
}
```

- [ ] **Step 2: compose-blocks.py**

```python
#!/usr/bin/env python3
"""Compose final composed.html from selections.yaml + prototype.yaml + tokens.json.

For each selection:
  1. Copy template.html (and template-mobile.html) of chosen block.
  2. Run inject-tokens.py to substitute CSS vars.
  3. Run inject-content.py to substitute texts from prototype.
  4. Concatenate all blocks into composed.html (desktop) and composed-mobile.html.

Output:
  <project>/07b_COMPOSED/composed.html
  <project>/07b_COMPOSED/composed-mobile.html
  <project>/07b_COMPOSED/block-injection-log.md
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--library", required=True)
    args = p.parse_args()

    project = Path(args.project)
    selections = yaml.safe_load((project / "07a_WIREFRAME" / "selections.yaml").read_text())
    proto = yaml.safe_load((project / "07_ПРОТОТИП" / "prototype.yaml").read_text())
    tokens_path = project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"

    library = Path(args.library)
    catalog = yaml.safe_load((library / "catalog.yaml").read_text())
    block_to_cat = {b["id"]: b["category"] for b in catalog["blocks"]}

    out_dir = project / "07b_COMPOSED"
    out_dir.mkdir(parents=True, exist_ok=True)

    scripts_dir = Path(__file__).parent
    inject_tokens = scripts_dir / "inject-tokens.py"
    inject_content = scripts_dir / "inject-content.py"

    desktop_parts: list[str] = []
    mobile_parts: list[str] = []
    log: list[str] = ["# Block injection log\n"]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        for sel in selections["selections"]:
            position = sel["block_position"]
            variant = sel["chosen_variant"]
            if variant not in block_to_cat:
                print(f"ERROR: variant {variant} not in catalog", file=sys.stderr)
                sys.exit(1)
            cat = block_to_cat[variant]
            block_dir = library / cat / variant

            for kind, suffix in (("desktop", "template.html"), ("mobile", "template-mobile.html")):
                src = block_dir / "assets" / suffix
                stage1 = tmp_p / f"{position}-{kind}-1.html"
                stage2 = tmp_p / f"{position}-{kind}-2.html"

                # 1. Inject tokens
                subprocess.run(
                    ["python3", str(inject_tokens), str(src), str(tokens_path), str(stage1)],
                    check=True,
                )
                # 2. Inject content
                subprocess.run(
                    ["python3", str(inject_content),
                     "--template", str(stage1),
                     "--prototype", str(project / "07_ПРОТОТИП" / "prototype.yaml"),
                     "--position", str(position),
                     "--output", str(stage2)],
                    check=True,
                )

                content = stage2.read_text()
                # Strip outer html/body — keep only inner section markup
                body_start = content.find("<body")
                body_close = content.rfind("</body>")
                if body_start != -1 and body_close != -1:
                    inner = content[content.find(">", body_start) + 1: body_close]
                else:
                    inner = content
                if kind == "desktop":
                    desktop_parts.append(f"<!-- block {position}: {variant} -->\n{inner}")
                else:
                    mobile_parts.append(f"<!-- block {position}: {variant} -->\n{inner}")

            log.append(f"- block {position}: `{variant}` — desktop+mobile injected, tokens applied")

    shell = (
        "<!DOCTYPE html><html lang='ru'><head><meta charset='UTF-8'>"
        "<title>Composed — {slug}</title></head><body>{body}</body></html>"
    )
    (out_dir / "composed.html").write_text(
        shell.format(slug=proto["project"]["slug"], body="\n".join(desktop_parts))
    )
    (out_dir / "composed-mobile.html").write_text(
        shell.format(slug=proto["project"]["slug"], body="\n".join(mobile_parts))
    )
    (out_dir / "block-injection-log.md").write_text("\n".join(log))

    print(f"OK: composed {len(selections['selections'])} blocks")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Запустить тесты — pass**

```bash
bats tests/phase-pra/test-compose-blocks.bats
```

- [ ] **Step 4: Commit**

```bash
git add skills/block-composition/scripts/compose-blocks.py tests/phase-pra/test-compose-blocks.bats
git commit -m "feat(block-composition): compose-blocks.py end-to-end + tests"
```

---

### Task 20: block-composer agent + /landing-compose command

**Files:**
- Create: `agents/block-composer.md`
- Create: `commands/landing-compose.md`

- [ ] **Step 1: agents/block-composer.md**

```markdown
---
name: block-composer
description: Use during stage 07b (Block Compose) to render composed.html — final pre-build assembly with design-tokens injected and prototype texts substituted. Visual content (photos/icons/infographics) remain as labeled placeholders (filled by PR-B/PR-C).
---

# block-composer

## Mission

Сборка `<project>/07b_COMPOSED/composed.html` + `composed-mobile.html` из утверждённых `selections.yaml`, `prototype.yaml` и `tokens.json`. На выходе — цветной макет с реальными текстами/CTA и visible placeholders для фото/иконок/инфографики.

## Inputs

- `<project>/07_ПРОТОТИП/prototype.yaml`
- `<project>/07a_WIREFRAME/selections.yaml`
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json`
- `block-library/` (общая)

## Workflow

1. Валидируй `selections.yaml`:
   ```bash
   python3 skills/block-composition/scripts/validate-selections.py 07a_WIREFRAME/selections.yaml
   ```
2. Запусти end-to-end composer:
   ```bash
   python3 skills/block-composition/scripts/compose-blocks.py \
       --project "$PWD" \
       --library "$LANDING_SYSTEM_ROOT/block-library"
   ```
3. Сообщи путь к `composed.html` пользователю.
4. Не делай больше ничего — финальный визуал (фото, иконки, инфографика) добавит PR-B/PR-C.

## CRITICAL

Если `selections.yaml` ссылается на блок, которого нет в `catalog.yaml` — STOP, сообщи пользователю.

## Tools

Read, Write, Bash.
```

- [ ] **Step 2: commands/landing-compose.md**

```markdown
---
description: Stage 07b — assemble composed.html with design-tokens injected and prototype content substituted. Visual placeholders remain.
---

# /landing-compose

Запускает этап **07b_COMPOSED**.

## Что делает

1. Проверяет наличие `07_ПРОТОТИП/prototype.yaml`, `07a_WIREFRAME/selections.yaml`, `05_ДИЗАЙН-СИСТЕМА/tokens.json`.
2. Передаёт работу агенту `block-composer`.
3. Сообщает путь к артефакту.

## Артефакты

- `07b_COMPOSED/composed.html`
- `07b_COMPOSED/composed-mobile.html`
- `07b_COMPOSED/block-injection-log.md`

## Условия запуска

- selections.yaml в `07a_WIREFRAME/` существует
- tokens.json в `05_ДИЗАЙН-СИСТЕМА/` существует

## NOTE (PR-A scope)

Не интегрировано в `landing-orchestrator` — задача PR-D.
Финальный визуальный контент (фото/иконки/инфографика) добавит PR-B/PR-C.
```

- [ ] **Step 3: bats тест**

```bash
cat >> tests/phase-pra/test-agents-exist.bats <<'EOF'

@test "block-composer agent file exists" {
  [ -f "$ROOT/agents/block-composer.md" ]
}

@test "landing-compose command file exists" {
  [ -f "$ROOT/commands/landing-compose.md" ]
}
EOF

bats tests/phase-pra/test-agents-exist.bats
```

- [ ] **Step 4: Commit**

```bash
git add agents/block-composer.md commands/landing-compose.md tests/phase-pra/test-agents-exist.bats
git commit -m "feat(agents,commands): block-composer + /landing-compose"
```

---

## Phase 7 — DESIGN.md 9-section update

### Task 21: Обновить design-tokens-generation skill под 9-секционную структуру

**Files:**
- Modify: `skills/design-tokens-generation/SKILL.md`
- Modify: `skills/design-tokens-generation/scripts/<existing generate script>` (если есть)

OpenDesign-G — 9 секций DESIGN.md: color / typography / spacing / layout / components / motion / voice / brand / anti-patterns. Текущий DESIGN.md покрывает 4-5 секций. Дополняем шаблон.

- [ ] **Step 1: Прочитать существующий SKILL.md**

```bash
cat skills/design-tokens-generation/SKILL.md
ls skills/design-tokens-generation/scripts/
```

- [ ] **Step 2: Найти текущий шаблон DESIGN.md (или место, где он определяется)**

```bash
grep -rn "DESIGN.md\|## Color\|## Typography" skills/design-tokens-generation/ | head -10
```

- [ ] **Step 3: Обновить SKILL.md секцией про 9-section format**

В конец `skills/design-tokens-generation/SKILL.md` добавить:

```markdown
## DESIGN.md output structure (updated 2026-05-12)

DESIGN.md теперь содержит 9 обязательных секций (формат заимствован у OpenDesign Apache-2.0 — см. THIRD_PARTY_NOTICES.md):

1. **## Color** — палитра + roles (bg/fg/accent/error/success), контрастные пары
2. **## Typography** — стек шрифтов (display/body/mono), масштаб (h1-h6, body, small), line-height
3. **## Spacing** — модульная сетка (xs/sm/md/lg/xl), правила отступов
4. **## Layout** — сетка (12 колонок), breakpoints (mobile/tablet/desktop), max-widths
5. **## Components** — стиль кнопок, инпутов, карточек, navbar
6. **## Motion** — duration tokens, easing curves, какие элементы анимируются
7. **## Voice** — тон коммуникации, длина текста, лексика (RU specific)
8. **## Brand** — что выражает бренд через визуал (3-5 ключевых атмосфер)
9. **## Anti-patterns** — чего НЕ делать в этом проекте (явный список)

Цель: глубина и предсказуемость как у Linear/Stripe/Notion (см. `vendor/opendesign-extracts/design-systems-refs/` для референсов — папка будет наполнена позже).
```

- [ ] **Step 4: Если есть `generate-design-md.py` или подобный — добавить заглушки секций 6-9 в шаблон**

```bash
# Найди шаблон
grep -rln "## Color" skills/design-tokens-generation/scripts/ template/ 2>/dev/null
```

Если нашёл такой файл — добавь в шаблон секции:
```markdown
## Motion

- duration-fast: 150ms
- duration-base: 250ms
- duration-slow: 400ms
- easing-standard: cubic-bezier(0.4, 0, 0.2, 1)
- easing-emphasis: cubic-bezier(0.4, 0, 0, 1)

Что анимируем: hover на CTA, открытие модалок, scroll-reveal.
Что НЕ анимируем: текстовые блоки, layout shifts.

## Voice

- Тон: <деловой / дружелюбный / экспертный>
- Лексика: <RU-литературная / RU-разговорная>
- Длина абзацев: до 3 предложений
- Заголовки: глагольная форма

## Brand

3-5 ключевых атмосфер, которые должен передавать сайт визуально и tonально.
Заполняется brand-architect.

## Anti-patterns

Чего НЕ делать в этом проекте (явный список):
- ...
```

- [ ] **Step 5: bats тест что новые секции упомянуты в SKILL.md**

```bash
cat > tests/phase-pra/test-design-md-sections.bats <<'EOF'
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
}

@test "design-tokens-generation SKILL.md mentions 9 sections" {
  run grep -c "^[0-9]\. \*\*## " "$ROOT/skills/design-tokens-generation/SKILL.md"
  [ "$status" -eq 0 ]
  [ "$output" -ge 9 ]
}

@test "SKILL.md references THIRD_PARTY_NOTICES" {
  run grep -l "THIRD_PARTY_NOTICES" "$ROOT/skills/design-tokens-generation/SKILL.md"
  [ "$status" -eq 0 ]
}
EOF

bats tests/phase-pra/test-design-md-sections.bats
```

- [ ] **Step 6: Commit**

```bash
git add skills/design-tokens-generation/ tests/phase-pra/test-design-md-sections.bats
git commit -m "feat(design-tokens-generation): adopt 9-section DESIGN.md structure (OpenDesign-derived)"
```

---

## Phase 8 — Docs + test runner

### Task 22: Обновить CLAUDE.md и добавить test script

**Files:**
- Modify: `CLAUDE.md`
- Modify: `package.json`

- [ ] **Step 1: Добавить в CLAUDE.md описание новых команд**

Прочитай текущий `CLAUDE.md`, найди раздел «Главные команды» или подобный. Добавь после существующих команд:

```markdown
## Новые команды PR-A (Прототип + Wireframe + Compose)

- `/landing-prototype` — импорт пользовательского прототипа (PDF/MD) → prototype.{md,yaml}
- `/landing-wireframe` — интерактивный wireframe.html с 2-3 вариантами на блок
- `/landing-compose` — composed.html с tokens + текстами, placeholders для визуала

**Workflow PR-A:**
1. Положи `prototype.pdf` или `.md` в `<project>/07_ПРОТОТИП/source/`
2. Запусти `/landing-prototype` → проверь `prototype.md`, поправь если нужно
3. Запусти `/landing-wireframe` → открой `07a_WIREFRAME/wireframe.html`, выбери варианты, нажми «Confirm» — скачается `selections.yaml`, положи его в `07a_WIREFRAME/`
4. Запусти `/landing-compose` → `07b_COMPOSED/composed.html` готов

**NOTE:** PR-A команды вызываются ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция в оркестратор — задача PR-D.

## Block Library

Общая библиотека wireframe-блоков: `block-library/`. См. `block-library/README.md`.

## Атрибуция

См. `THIRD_PARTY_NOTICES.md` — мы используем фрагменты OpenDesign (Apache-2.0).
```

- [ ] **Step 2: package.json — добавить test:phase-pra**

```json
"test:phase-pra": "bats tests/phase-pra/*.bats"
```

Используй Edit для добавления строки в `scripts` блок:

```bash
# Найди строку с test:phase-preview-panel и добавь после неё
```

- [ ] **Step 3: Запустить все тесты разом**

```bash
npm run test:phase-pra
```

Ожидаемо: все тесты PASS.

- [ ] **Step 4: Запустить full test suite**

```bash
npm test
```

Если что-то падает — проверь что добавленные тесты не ломают другие фазы.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md package.json
git commit -m "docs(claude): document PR-A commands + block-library + add test:phase-pra"
```

---

## Final acceptance check

После выполнения всех задач — финальная sanity-проверка:

```bash
cd "$(git rev-parse --show-toplevel)"

# 1. Все 17 блоков на месте
test "$(find block-library -name meta.yaml | wc -l | tr -d ' ')" = "17" || echo "FAIL: not 17 blocks"

# 2. catalog.yaml валидируется
python3 skills/block-library-management/scripts/validate-catalog.py block-library/catalog.yaml

# 3. Каждый meta.yaml валидируется
for d in block-library/*/*/meta.yaml; do
  python3 skills/block-library-management/scripts/validate-meta.py "$d" || echo "FAIL: $d"
done

# 4. Все bats тесты проходят
npm run test:phase-pra

# 5. Новые агенты и команды на месте
test -f agents/prototype-importer.md && \
test -f agents/ux-composer.md && \
test -f agents/block-composer.md && \
test -f commands/landing-prototype.md && \
test -f commands/landing-wireframe.md && \
test -f commands/landing-compose.md && echo "OK"

# 6. THIRD_PARTY_NOTICES.md существует
test -f THIRD_PARTY_NOTICES.md && echo "OK"

# 7. OpenDesign extracts scaffold
test -f vendor/opendesign-extracts/LICENSE && \
test -f vendor/opendesign-extracts/ATTRIBUTION.md && echo "OK"

# 8. Template папки добавлены
test -d template/07_ПРОТОТИП && \
test -d template/07a_WIREFRAME && \
test -d template/07b_COMPOSED && echo "OK"

echo "✅ PR-A acceptance: all checks passed"
```

---

## Self-review notes (для исполнителя)

Этот план содержит 22 задачи. После каждой — commit. Если subagent-driven запускается, типичный путь:

1. Task 1-3 (foundation) — sequential, быстро.
2. Tasks 4-7 (validators) — могут идти параллельно (4 параллельных subagent dispatch).
3. Task 8 (scaffolder) — после Task 5 (нужен validate-meta).
4. Task 9 (seed blocks) — тяжёлая, последовательная внутри. Требует Tasks 3, 5, 8.
5. Tasks 10-13 (prototype-import) — могут идти параллельно с seed blocks.
6. Tasks 14-16 (wireframe) — требуют seed blocks готовы.
7. Tasks 17-20 (compose) — требуют tasks 14-16.
8. Tasks 21-22 (docs+design-md) — финал, могут идти параллельно с compose.

Recommended subagent strategy: dispatch foundation, потом ferment 2 parallel tracks (validators+scaffolder vs prototype-import scripts), потом seed blocks отдельно, потом compose цепочка, потом docs.
