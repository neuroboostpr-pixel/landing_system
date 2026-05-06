# Niche Analysis Stage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Встроить новый этап `01a_АНАЛИЗ_НИШИ` между этапами 01 и 02, с автоматическим агентом `niche-analyst`, который собирает 15–25 конкурентов в 7 ролях и выдаёт три артефакта на русском языке.

**Architecture:** Один агент с tools (WebSearch + Firecrawl MCP + Read/Write), zero-touch для пользователя. Этап вставляется как `01a` без сдвига нумерации остальных этапов. Backward-compatible через optional flag в `stage-gates.yaml`. Контракт читателей (brand-architect, content-writer и др.) обновляется отдельными правками.

**Tech Stack:** Bash + bats для тестов скриптов, Python для валидации YAML схемы конкурентов, существующий `gate-check.sh`/`gate-state.sh`, агенты Claude Code (Markdown frontmatter), Firecrawl MCP.

**Spec source:** [`docs/superpowers/specs/2026-05-06-niche-analysis-design.md`](../specs/2026-05-06-niche-analysis-design.md)

---

## File Structure

**Создаются:**
- `template/01a_АНАЛИЗ_НИШИ/.gitkeep` — папка появляется в шаблоне
- `template/01a_АНАЛИЗ_НИШИ/README.md` — описание этапа
- `agents/niche-analyst.md` — новый агент
- `commands/landing-niche.md` — slash-команда (плагин-источник)
- `.claude/commands/landing-niche.md` — копия для локального использования
- `skills/niche-analysis/SKILL.md` — оборачивающий skill (запускается командой)
- `skills/niche-analysis/scripts/validate-competitors.py` — валидатор схемы YAML
- `tests/phase-niche/test-niche-stage.bats` — bats-тесты этапа
- `tests/phase-niche/test-validate-competitors.py` — pytest-тесты валидатора
- `tests/phase-niche/fixtures/competitors-valid.yaml` — фикстура валидного файла
- `tests/phase-niche/fixtures/competitors-invalid-too-few.yaml` — фикстура с <15 записями
- `tests/phase-niche/fixtures/competitors-invalid-bad-role.yaml` — фикстура с неверным role

**Модифицируются:**
- `template/.landing-state.yaml` — добавить ключ `01a_niche_analysis`
- `template/CLAUDE.md` — обновить таблицу с 12 → 13 этапов
- `config/stage-gates.yaml` — добавить блок `01a_niche_analysis` + поправить `02_assets.require_approved`
- `agents/landing-orchestrator.md` — добавить переход 01 → 01a → 02
- `agents/references-curator.md` — добавить чтение `competitors.yaml`
- `agents/moodboard-composer.md` — добавить чтение `niche-analysis.md`
- `agents/brand-architect.md` — добавить чтение `positioning.md`
- `agents/content-writer.md` — добавить чтение `positioning.md` + `competitors.yaml`
- `agents/seo-optimizer.md` — добавить чтение `competitors.yaml`
- `README.md` — обновить таблицу команд + статус-таблицу stages
- `docs/SETUP.md` — упомянуть новый этап (если ссылается на список)
- `package.json` — добавить script `test:phase-niche` (если есть аналогичные)

---

## Task 1: Папка и README в шаблоне

**Files:**
- Create: `template/01a_АНАЛИЗ_НИШИ/.gitkeep`
- Create: `template/01a_АНАЛИЗ_НИШИ/README.md`

- [ ] **Step 1: Write the failing bats test**

Create `tests/phase-niche/test-niche-stage.bats`:

```bash
#!/usr/bin/env bats

setup() {
  TEMPLATE_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template" && pwd)"
}

@test "template has 01a_АНАЛИЗ_НИШИ folder" {
  [ -d "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ" ]
}

@test "template 01a folder has README" {
  [ -f "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md" ]
}

@test "template 01a README mentions three artifacts" {
  grep -q "niche-analysis.md" "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md"
  grep -q "competitors.yaml" "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md"
  grep -q "positioning.md" "$TEMPLATE_DIR/01a_АНАЛИЗ_НИШИ/README.md"
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: 3 tests fail with "no such file or directory" / similar.

- [ ] **Step 3: Create folder + .gitkeep**

```bash
mkdir -p template/01a_АНАЛИЗ_НИШИ
touch template/01a_АНАЛИЗ_НИШИ/.gitkeep
```

- [ ] **Step 4: Create README.md**

Create `template/01a_АНАЛИЗ_НИШИ/README.md`:

```markdown
# 01a. Анализ ниши

Этап автоматического исследования: что за продукт, какой тип бренда, кто конкуренты, на что давим.

## Артефакты

- `niche-analysis.md` — нарративный отчёт (400–800 слов): тип бренда, описание ниши, рекомендация «на что давим», список допущений.
- `competitors.yaml` — машиночитаемая база 15–25 игроков в 7 ролях: direct, local_dealer, manufacturer, analog, category_leader, local_competitor, indirect.
- `positioning.md` — единый источник истины для следующих этапов: core promise, tone of voice, 1–2 угла отстройки, чего избегать.

## Кто пишет

Агент `niche-analyst`. Запускается командой `/landing-niche`.

## Что читает

- `00_БРИФ/brief.md` (обязательно)
- `01_КОНТЕКСТ/context.md` (если есть)

## Что читает после

- `references-curator` (этап 03) — `competitors.yaml`
- `moodboard-composer` (этап 03) — `niche-analysis.md`
- `brand-architect` (этап 04) — `positioning.md`
- `content-writer` (этап 07) — `positioning.md` + `competitors.yaml`
- `seo-optimizer` (этап 12) — `competitors.yaml`

## Принцип

Zero-touch: пользователь не отвечает на вопросы агента. При нехватке данных агент помечает поля `[ДОПУЩЕНИЕ]`.

## Язык

Все значения полей и тексты на русском. Имена ключей YAML/Markdown на английском. Имена брендов и URL без транслита.
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add template/01a_АНАЛИЗ_НИШИ/ tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): scaffold template folder + README"
```

---

## Task 2: Расширить .landing-state.yaml

**Files:**
- Modify: `template/.landing-state.yaml`
- Modify: `tests/phase-niche/test-niche-stage.bats` (add test)

- [ ] **Step 1: Add failing test**

Append to `tests/phase-niche/test-niche-stage.bats`:

```bash
@test "landing-state template has 01a_niche_analysis stage" {
  grep -q '"01a_niche_analysis"' "$TEMPLATE_DIR/.landing-state.yaml"
}

@test "landing-state 01a is locked initially" {
  grep -E '"01a_niche_analysis":\s+\{status: locked' "$TEMPLATE_DIR/.landing-state.yaml"
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: 2 new tests FAIL.

- [ ] **Step 3: Add stage to landing-state template**

Edit `template/.landing-state.yaml` — add line between `01_context` and `02_assets`:

```yaml
stages:
  "00_brief":             {status: in_progress, timestamp: ""}
  "01_context":           {status: locked, timestamp: ""}
  "01a_niche_analysis":   {status: locked, timestamp: ""}
  "02_assets":            {status: locked, timestamp: ""}
  "03_references":        {status: locked, timestamp: ""}
  "04_brand":             {status: locked, timestamp: ""}
  "05_design":            {status: locked, timestamp: ""}
  "06_stack":             {status: locked, timestamp: ""}
  "07_content":           {status: locked, timestamp: ""}
  "08_build":             {status: locked, timestamp: ""}
  "09_deploy":            {status: locked, timestamp: ""}
  "10_qa":                {status: locked, timestamp: ""}
  "11_analytics":         {status: locked, timestamp: ""}
  "12_seo":               {status: locked, timestamp: ""}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add template/.landing-state.yaml tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): add 01a_niche_analysis to landing-state template"
```

---

## Task 3: stage-gates.yaml блок и зависимость 02_assets

**Files:**
- Modify: `config/stage-gates.yaml`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Add failing test**

Append to `tests/phase-niche/test-niche-stage.bats`:

```bash
@test "stage-gates has 01a_niche_analysis block" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q '"01a_niche_analysis":' "$GATES"
}

@test "stage-gates 02_assets requires 01a_niche_analysis approved" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  yq -e '.stages."02_assets".require_approved | contains(["01a_niche_analysis"])' "$GATES"
}

@test "stage-gates 01a hard checks include three artifacts" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "niche-analysis.md" "$GATES"
  grep -q "competitors.yaml" "$GATES"
  grep -q "positioning.md" "$GATES"
}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: 3 new tests FAIL.

- [ ] **Step 3: Edit config/stage-gates.yaml**

Insert new block between `02_assets` and `03_references` (before `02_assets`'s body, after `00_brief`). Add it right after `00_brief` block but before existing `02_assets`:

```yaml
  "01a_niche_analysis":
    name: "Niche analysis"
    require_approved: ["00_brief"]
    hard_checks:
      - id: niche_analysis_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/niche-analysis.md"
        required: true
        fix_hint: "niche-analyst agent creates this"
      - id: competitors_yaml
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/competitors.yaml"
        required: true
        fix_hint: "niche-analyst agent creates this"
      - id: positioning_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/positioning.md"
        required: true
        fix_hint: "niche-analyst agent creates this"
      - id: competitors_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-competitors.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/competitors.yaml"]
        required: true
        fix_hint: "Fix competitors.yaml — see script output for issues"
    soft_checks:
      - id: positioning_max_2_angles
        prompt: "В positioning.md ровно 1 или 2 угла отстройки (не больше)? (yes / no)"
      - id: competitors_count_15_25
        prompt: "В competitors.yaml 15–25 записей? (yes / no)"
```

Then in the existing `02_assets` block, change:
```yaml
    require_approved: ["00_brief", "01_context"]
```
to:
```yaml
    require_approved: ["00_brief", "01_context", "01a_niche_analysis"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: all PASS. If `yq -e` fails on Windows, install yq or skip that one specific test on Windows.

- [ ] **Step 5: Commit**

```bash
git add config/stage-gates.yaml tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): stage-gates block + 02_assets dependency"
```

---

## Task 4: Валидатор схемы competitors.yaml

**Files:**
- Create: `skills/niche-analysis/scripts/validate-competitors.py`
- Create: `tests/phase-niche/test-validate-competitors.py`
- Create: `tests/phase-niche/fixtures/competitors-valid.yaml`
- Create: `tests/phase-niche/fixtures/competitors-invalid-too-few.yaml`
- Create: `tests/phase-niche/fixtures/competitors-invalid-bad-role.yaml`

- [ ] **Step 1: Create three fixtures**

Create `tests/phase-niche/fixtures/competitors-valid.yaml` (15 valid entries — minimum required):

```yaml
competitors:
  - {name: "Конкурент 1",  role: direct,           url: "https://e1.com",  region: "ОАЭ",       positioning: "p1",  target_audience: "ЦА1",  price_range: "1",  key_messages: ["m1"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 2",  role: direct,           url: "https://e2.com",  region: "ОАЭ",       positioning: "p2",  target_audience: "ЦА2",  price_range: "2",  key_messages: ["m2"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 3",  role: direct,           url: "https://e3.com",  region: "ОАЭ",       positioning: "p3",  target_audience: "ЦА3",  price_range: "3",  key_messages: ["m3"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 4",  role: local_dealer,     url: "https://e4.com",  region: "РФ",        positioning: "p4",  target_audience: "ЦА4",  price_range: "4",  key_messages: ["m4"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 5",  role: manufacturer,     url: "https://e5.com",  region: "global",    positioning: "p5",  target_audience: "ЦА5",  price_range: "5",  key_messages: ["m5"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 6",  role: analog,           url: "https://e6.com",  region: "ОАЭ",       positioning: "p6",  target_audience: "ЦА6",  price_range: "6",  key_messages: ["m6"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: medium}
  - {name: "Конкурент 7",  role: analog,           url: "https://e7.com",  region: "ОАЭ",       positioning: "p7",  target_audience: "ЦА7",  price_range: "7",  key_messages: ["m7"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: medium}
  - {name: "Конкурент 8",  role: category_leader,  url: "https://e8.com",  region: "global",    positioning: "p8",  target_audience: "ЦА8",  price_range: "8",  key_messages: ["m8"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 9",  role: local_competitor, url: "https://e9.com",  region: "ОАЭ",       positioning: "p9",  target_audience: "ЦА9",  price_range: "9",  key_messages: ["m9"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: medium}
  - {name: "Конкурент 10", role: local_competitor, url: "https://e10.com", region: "ОАЭ",       positioning: "p10", target_audience: "ЦА10", price_range: "10", key_messages: ["m10"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: low}
  - {name: "Конкурент 11", role: indirect,         url: "https://e11.com", region: "ОАЭ",       positioning: "p11", target_audience: "ЦА11", price_range: "11", key_messages: ["m11"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: low}
  - {name: "Конкурент 12", role: direct,           url: "https://e12.com", region: "ОАЭ",       positioning: "p12", target_audience: "ЦА12", price_range: "12", key_messages: ["m12"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 13", role: direct,           url: "https://e13.com", region: "ОАЭ",       positioning: "p13", target_audience: "ЦА13", price_range: "13", key_messages: ["m13"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Конкурент 14", role: local_competitor, url: "https://e14.com", region: "ОАЭ",       positioning: "p14", target_audience: "ЦА14", price_range: "14", key_messages: ["m14"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: medium}
  - {name: "Конкурент 15", role: local_competitor, url: "https://e15.com", region: "ОАЭ",       positioning: "p15", target_audience: "ЦА15", price_range: "15", key_messages: ["m15"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: medium}
```

Create `tests/phase-niche/fixtures/competitors-invalid-too-few.yaml` (10 entries, all role=direct — fails minimum 15 + role diversity):

```yaml
competitors:
  - {name: "X1", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X2", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X3", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X4", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X5", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X6", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X7", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X8", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X9", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "X10", role: direct, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
```

Create `tests/phase-niche/fixtures/competitors-invalid-bad-role.yaml` (15 entries, one with bad role):

```yaml
competitors:
  - {name: "Y1",  role: NOT_A_REAL_ROLE, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y2",  role: direct,    url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y3",  role: direct,    url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y4",  role: analog,    url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y5",  role: analog,    url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y6",  role: indirect,  url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y7",  role: indirect,  url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y8",  role: manufacturer, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y9",  role: local_dealer, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y10", role: category_leader, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y11", role: local_competitor, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y12", role: local_competitor, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y13", role: direct,    url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y14", role: local_competitor, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
  - {name: "Y15", role: local_competitor, url: "u", region: "r", positioning: "p", target_audience: "a", price_range: "x", key_messages: ["m"], visual_notes: "n", notes_for_us: "u", source: "s", confidence: high}
```

- [ ] **Step 2: Write the failing pytest**

Create `tests/phase-niche/test-validate-competitors.py`:

```python
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-competitors.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(fixture_name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / fixture_name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("competitors-valid.yaml")
    assert r.returncode == 0, r.stderr


def test_too_few_fails():
    r = run("competitors-invalid-too-few.yaml")
    assert r.returncode != 0
    assert "minimum 15" in (r.stdout + r.stderr).lower() or "15" in r.stdout + r.stderr


def test_bad_role_fails():
    r = run("competitors-invalid-bad-role.yaml")
    assert r.returncode != 0
    assert "role" in (r.stdout + r.stderr).lower()
```

- [ ] **Step 3: Run pytest to verify it fails**

Run: `python -m pytest tests/phase-niche/test-validate-competitors.py -v`
Expected: 3 tests FAIL — script doesn't exist yet.

- [ ] **Step 4: Implement validator**

Create `skills/niche-analysis/scripts/validate-competitors.py`:

```python
#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/competitors.yaml against schema.

Exits 0 on valid, 1 on errors with messages on stdout.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

VALID_ROLES = {
    "direct", "local_dealer", "manufacturer", "analog",
    "category_leader", "local_competitor", "indirect",
}
VALID_CONFIDENCE = {"high", "medium", "low"}
REQUIRED_FIELDS = {
    "name", "role", "url", "region", "positioning", "target_audience",
    "price_range", "key_messages", "visual_notes", "notes_for_us",
    "source", "confidence",
}
MIN_COUNT = 15
MAX_COUNT = 25


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict) or "competitors" not in data:
        return ["Top-level must be a mapping with key 'competitors'"]

    items = data["competitors"]
    if not isinstance(items, list):
        return ["'competitors' must be a list"]

    n = len(items)
    if n < MIN_COUNT:
        errors.append(f"Need minimum 15 entries, got {n}")
    if n > MAX_COUNT:
        errors.append(f"Maximum 25 entries allowed, got {n}")

    seen_roles = set()
    for i, entry in enumerate(items):
        if not isinstance(entry, dict):
            errors.append(f"Entry {i}: must be a mapping")
            continue
        missing = REQUIRED_FIELDS - set(entry.keys())
        if missing:
            errors.append(f"Entry {i} ({entry.get('name', '?')}): missing fields {sorted(missing)}")
        role = entry.get("role")
        if role not in VALID_ROLES:
            errors.append(f"Entry {i} ({entry.get('name', '?')}): invalid role '{role}', must be one of {sorted(VALID_ROLES)}")
        else:
            seen_roles.add(role)
        conf = entry.get("confidence")
        if conf not in VALID_CONFIDENCE:
            errors.append(f"Entry {i} ({entry.get('name', '?')}): invalid confidence '{conf}'")

    if len(seen_roles) < 3:
        errors.append(f"Need at least 3 different roles, got {len(seen_roles)}: {sorted(seen_roles)}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-competitors.py <competitors.yaml>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("competitors.yaml validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run pytest to verify all pass**

Run: `python -m pytest tests/phase-niche/test-validate-competitors.py -v`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/niche-analysis/scripts/validate-competitors.py tests/phase-niche/test-validate-competitors.py tests/phase-niche/fixtures/
git commit -m "feat(stage-01a): competitors.yaml schema validator + tests"
```

---

## Task 5: Агент niche-analyst

**Files:**
- Create: `agents/niche-analyst.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Add failing test**

Append to `tests/phase-niche/test-niche-stage.bats`:

```bash
@test "niche-analyst agent file exists" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  [ -f "$AGENT" ]
}

@test "niche-analyst has frontmatter with name and description" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "^name: niche-analyst" "$AGENT"
  grep -q "^description:" "$AGENT"
}

@test "niche-analyst mentions all 7 roles" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  for role in direct local_dealer manufacturer analog category_leader local_competitor indirect; do
    grep -q "$role" "$AGENT" || { echo "missing role: $role"; return 1; }
  done
}

@test "niche-analyst documents zero-touch principle" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -qi "zero-touch\|никаких вопросов\|без вопросов" "$AGENT"
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: 4 new tests FAIL.

- [ ] **Step 3: Create agents/niche-analyst.md**

```markdown
---
name: niche-analyst
description: Use during stage 01a to automatically research the niche and competitors. Reads 00_БРИФ/brief.md and 01_КОНТЕКСТ/context.md (if present), classifies brand type (1/2/3), collects 15-25 competitors across 7 roles via WebSearch + Firecrawl, writes niche-analysis.md, competitors.yaml, positioning.md to 01a_АНАЛИЗ_НИШИ/. Zero-touch — does not ask the user clarifying questions; marks gaps as [ДОПУЩЕНИЕ].
---

# niche-analyst

## Mission

Stage 01a (между 01_КОНТЕКСТ и 02_МАТЕРИАЛЫ_КЛИЕНТА). Сделать автоматический ресёрч ниши и выдать три артефакта на русском языке.

## Принцип

**Zero-touch.** Никаких уточняющих вопросов пользователю. При нехватке данных — пометка `[ДОПУЩЕНИЕ]` в нужном поле и `confidence: low/medium`.

## Входы

- `00_БРИФ/brief.md` — обязательно
- `01_КОНТЕКСТ/context.md` — если есть

## Выходы (в `01a_АНАЛИЗ_НИШИ/`)

1. `niche-analysis.md` — 400–800 слов: тип бренда, описание ниши, рекомендация «на что давим», список допущений.
2. `competitors.yaml` — 15–25 записей в 7 ролях: direct, local_dealer, manufacturer, analog, category_leader, local_competitor, indirect. Схема в `skills/niche-analysis/scripts/validate-competitors.py`.
3. `positioning.md` — core promise, tone of voice, 1–2 угла отстройки, чего избегать.

## Алгоритм

1. **Парсинг входов.** Извлечь: название бренда/продукта, категорию, регион, язык брифа, целевой рынок.

2. **Язык и регион поиска.**
   - Язык запросов = язык брифа.
   - Регион = целевой рынок (Dubai → google.com + UAE; Россия → google.ru + Я.Карты; Лагос → google.com.ng).

3. **Классификация типа бренда** по сигналам (НЕ по языку брифа):
   - WebSearch: `"<brand>" wikipedia` — на скольки языках?
   - WebSearch: общий объём результатов
   - Решение:
     - Wikipedia ≥3 языков + brand book → **Тип 1 (глобальный)**
     - Wikipedia 1–2 языков ИЛИ >5k упоминаний → **Тип 2 (региональный)**
     - Иначе → **Тип 3 (локальный без бренда)**
   - Английский бриф ≠ глобальный бренд. Локальная стоматология в Лагосе — Тип 3.

4. **Сбор конкурентов** по типу (см. spec §4.2 шаг 4):
   - Тип 1: manufacturer 1, local_dealer 1–3, direct 5, local_competitor 3, analog 2, category_leader 1, indirect 1
   - Тип 2: manufacturer 0–1, direct 5, local_competitor 5, analog 2, category_leader 1, indirect 1–2
   - Тип 3: local_competitor 8–10, category_leader 1, indirect 2, direct 2–3
   - Минимум суммарно: 15 записей, минимум 3 разных role.

5. **Скрейп каждого конкурента** через `mcp__firecrawl__scrape`. Извлечь: positioning (h1/hero), key_messages (выделенные блоки), price_range, target_audience, visual_notes (по описанию контента).

6. **Синтез позиционирования.**
   - Найти повторяющиеся темы у всех конкурентов → туда нельзя.
   - Найти gaps → кандидаты на угол отстройки.
   - Свести с УТП клиента из брифа → выбрать 1–2 угла.

7. **Запись артефактов** в `01a_АНАЛИЗ_НИШИ/`. Все значения и тексты на русском, имена ключей и брендов как есть.

8. **Самопроверка.** Запустить `python skills/niche-analysis/scripts/validate-competitors.py 01a_АНАЛИЗ_НИШИ/competitors.yaml`. Если errors — исправить и повторить.

## Tools

WebSearch, mcp__firecrawl__scrape, Read, Write, Bash (только для запуска валидатора).

Не использует: Edit, ssh, scp, ничего на удалённых серверах.

## Hand-off

После записи артефактов → `landing-orchestrator` проверяет gate-check и спрашивает у пользователя approval для перехода 01a → 02.
```

- [ ] **Step 4: Run tests to verify all pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add agents/niche-analyst.md tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): niche-analyst agent"
```

---

## Task 6: Slash-команда /landing-niche

**Files:**
- Create: `commands/landing-niche.md`
- Create: `.claude/commands/landing-niche.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Add failing test**

Append:

```bash
@test "landing-niche command exists in commands/" {
  CMD="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../commands" && pwd)/landing-niche.md"
  [ -f "$CMD" ]
}

@test "landing-niche command exists in .claude/commands/" {
  CMD="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.claude/commands" && pwd)/landing-niche.md"
  [ -f "$CMD" ]
}

@test "landing-niche command files are identical" {
  A="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../commands" && pwd)/landing-niche.md"
  B="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.claude/commands" && pwd)/landing-niche.md"
  diff -q "$A" "$B"
}

@test "landing-niche invokes niche-analyst agent" {
  CMD="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../commands" && pwd)/landing-niche.md"
  grep -q "niche-analyst" "$CMD"
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: 4 new tests FAIL.

- [ ] **Step 3: Create commands/landing-niche.md**

```markdown
---
description: Run niche analysis (stage 01a) for current landing project. Reads brief and context, outputs niche-analysis.md, competitors.yaml, positioning.md.
---

# /landing-niche

Запустить этап **01a_АНАЛИЗ_НИШИ** для текущего проекта-лендинга.

## Что делает

1. Запускает gate-check этапа `00_brief` → должен быть `approved`.
2. Если этап `01a_niche_analysis` уже `approved` — спрашивает подтверждение перезапуска.
3. Помечает этап `01a_niche_analysis` как `in_progress`.
4. Передаёт работу агенту `niche-analyst`.
5. После записи артефактов запускает `python skills/niche-analysis/scripts/validate-competitors.py`.
6. Запускает `bash scripts/gate-check.sh --stage 01a_niche_analysis --project <PWD>`.
7. Если все hard-checks прошли — показывает summary и спрашивает approval для перехода на 02.

## Артефакты после выполнения

- `01a_АНАЛИЗ_НИШИ/niche-analysis.md`
- `01a_АНАЛИЗ_НИШИ/competitors.yaml`
- `01a_АНАЛИЗ_НИШИ/positioning.md`

## Условия запуска

- Onboarding пройден (`~/.landing-system/setup_complete`)
- Текущая папка содержит `.landing-state.yaml`
- Этап `00_brief` имеет статус `approved`

## Принцип

Агент работает zero-touch — не задаёт уточняющих вопросов. Все недостающие данные помечаются `[ДОПУЩЕНИЕ]`.
```

- [ ] **Step 4: Copy to .claude/commands/**

```bash
cp commands/landing-niche.md .claude/commands/landing-niche.md
```

- [ ] **Step 5: Run tests to verify all pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add commands/landing-niche.md .claude/commands/landing-niche.md tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): /landing-niche slash command"
```

---

## Task 7: Skill-обёртка niche-analysis

**Files:**
- Create: `skills/niche-analysis/SKILL.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Add failing test**

Append:

```bash
@test "niche-analysis SKILL.md exists" {
  SKILL="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../skills" && pwd)/niche-analysis/SKILL.md"
  [ -f "$SKILL" ]
}

@test "niche-analysis SKILL has frontmatter" {
  SKILL="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../skills" && pwd)/niche-analysis/SKILL.md"
  grep -q "^name:" "$SKILL"
  grep -q "^description:" "$SKILL"
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bats tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 3: Create skills/niche-analysis/SKILL.md**

```markdown
---
name: niche-analysis
description: Stage 01a — automatic niche and competitor research. Invoked by /landing-niche command. Hands off to niche-analyst agent. Outputs three artifacts in 01a_АНАЛИЗ_НИШИ/. Zero-touch.
---

# niche-analysis skill

Обёртка вокруг агента `niche-analyst` для запуска через slash-команду `/landing-niche`.

## Что делает skill

1. Проверяет, что текущая папка — это проект-лендинг (`.landing-state.yaml` существует).
2. Проверяет, что этап `00_brief` имеет статус `approved`.
3. Помечает `01a_niche_analysis` как `in_progress` через `scripts/gate-state.sh`.
4. Делегирует работу агенту `niche-analyst`.
5. После завершения работы агента запускает валидатор schema и `gate-check.sh`.

## Файлы

- `scripts/validate-competitors.py` — валидатор схемы YAML

## См. также

- Агент: `agents/niche-analyst.md`
- Spec: `docs/superpowers/specs/2026-05-06-niche-analysis-design.md`
```

- [ ] **Step 4: Run tests to verify all pass**

- [ ] **Step 5: Commit**

```bash
git add skills/niche-analysis/SKILL.md tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): niche-analysis skill wrapper"
```

---

## Task 8: Подключить этап в landing-orchestrator

**Files:**
- Modify: `agents/landing-orchestrator.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Read current orchestrator**

Run: `cat agents/landing-orchestrator.md`
Note where the stage list / transitions are defined.

- [ ] **Step 2: Add failing test**

Append:

```bash
@test "orchestrator knows about 01a_niche_analysis" {
  ORC="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/landing-orchestrator.md"
  grep -q "01a_niche_analysis\|01a_АНАЛИЗ_НИШИ" "$ORC"
}

@test "orchestrator transitions 01 -> 01a -> 02" {
  ORC="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/landing-orchestrator.md"
  grep -q "niche-analyst" "$ORC"
}
```

- [ ] **Step 3: Run tests to verify they fail**

- [ ] **Step 4: Edit agents/landing-orchestrator.md**

Find the stage table or transition list. Insert a row/entry for `01a` between `01_context` and `02_assets`. Use exact existing format. Example insertion (adapt to actual structure):

```markdown
| 01a | 01a_АНАЛИЗ_НИШИ | niche-analyst | автоматический ресёрч ниши + 15–25 конкурентов |
```

And in the transitions/process section, add: «После одобрения 01_context → запустить niche-analyst (этап 01a). После одобрения 01a → этап 02_assets».

- [ ] **Step 5: Run tests to verify all pass**

- [ ] **Step 6: Commit**

```bash
git add agents/landing-orchestrator.md tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): wire niche-analysis into landing-orchestrator"
```

---

## Task 9: Контракты с downstream-агентами

**Files:**
- Modify: `agents/references-curator.md`
- Modify: `agents/moodboard-composer.md`
- Modify: `agents/brand-architect.md`
- Modify: `agents/content-writer.md`
- Modify: `agents/seo-optimizer.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Add failing tests**

Append:

```bash
@test "references-curator reads competitors.yaml" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/references-curator.md"
  grep -q "competitors.yaml\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "moodboard-composer reads niche-analysis.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/moodboard-composer.md"
  grep -q "niche-analysis.md\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "brand-architect reads positioning.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/brand-architect.md"
  grep -q "positioning.md\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}

@test "content-writer reads positioning.md and competitors.yaml" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/content-writer.md"
  grep -q "positioning.md" "$AGENT"
  grep -q "competitors.yaml" "$AGENT"
}

@test "seo-optimizer reads competitors.yaml" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/seo-optimizer.md"
  grep -q "competitors.yaml\|01a_АНАЛИЗ_НИШИ" "$AGENT"
}
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Edit each agent file**

In each file, add a section in the «Inputs» / «Process» area:

For `references-curator.md`, append:
```markdown

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — обязательный input. Поле `visual_notes` каждого конкурента читать перед поиском референсов: не клонировать визуал лидеров категории, искать gaps.
```

For `moodboard-composer.md`, append:
```markdown

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/niche-analysis.md` — обязательный input. Section 6 «Что брать с собой в следующие этапы» определяет, какой визуальный язык уместен.
```

For `brand-architect.md`, append:
```markdown

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/positioning.md` — обязательный input. Это единый источник истины: core promise, tone of voice, углы отстройки. Не переизобретать позиционирование, использовать готовое.
```

For `content-writer.md`, append:
```markdown

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/positioning.md` — обязательный input. Использовать сообщения углов отстройки в текстах блоков.
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `key_messages` каждой записи. Не повторять сообщения, которые говорят все конкуренты (см. секцию «Чего избегать» в positioning.md).
```

For `seo-optimizer.md`, append:
```markdown

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `key_messages`. Использовать как источник семантики и ключевых слов.
```

- [ ] **Step 4: Run tests to verify all pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 5: Commit**

```bash
git add agents/references-curator.md agents/moodboard-composer.md agents/brand-architect.md agents/content-writer.md agents/seo-optimizer.md tests/phase-niche/test-niche-stage.bats
git commit -m "feat(stage-01a): downstream agents read niche-analysis artifacts"
```

---

## Task 10: Документация — README + template/CLAUDE.md

**Files:**
- Modify: `README.md`
- Modify: `template/CLAUDE.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Add failing tests**

Append:

```bash
@test "root README mentions /landing-niche command" {
  README="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)/README.md"
  grep -q "/landing-niche" "$README"
}

@test "template CLAUDE.md mentions stage 01a" {
  CL="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template" && pwd)/CLAUDE.md"
  grep -q "01a_АНАЛИЗ_НИШИ\|01a" "$CL"
}
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Edit README.md**

In the commands table, insert before `/landing-references`:

```markdown
| `/landing-niche` | Анализ ниши и конкурентов (этап 01a) |
```

In the Status section's stage list, add row 01a between «1. Skeleton» and «2. Brainstorming Pipeline». In the «Stages (этапы 00–12)» description, change to «00–12 + 01a».

- [ ] **Step 4: Edit template/CLAUDE.md**

In the table, insert row between 01 and 02:

```markdown
| 01a | `01a_АНАЛИЗ_НИШИ/` | Анализ ниши, типа бренда, конкурентов |
```

Update the «12 этапов workflow» heading to «13 этапов workflow».

- [ ] **Step 5: Run tests to verify all pass**

- [ ] **Step 6: Commit**

```bash
git add README.md template/CLAUDE.md tests/phase-niche/test-niche-stage.bats
git commit -m "docs(stage-01a): README + template CLAUDE.md updated"
```

---

## Task 11: End-to-end smoke test

**Files:**
- Create: `tests/phase-niche/test-e2e-skip-prevention.bats`

- [ ] **Step 1: Write failing e2e test**

Create `tests/phase-niche/test-e2e-skip-prevention.bats`:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  TMP="$(mktemp -d)"
  PROJECT="$TMP/test-niche-project"
  mkdir -p "$PROJECT"
  cp -r "$REPO/template/." "$PROJECT/"
  # Mark only 00_brief as approved
  yq -i '.stages."00_brief".status = "approved"' "$PROJECT/.landing-state.yaml"
}

teardown() {
  rm -rf "$TMP"
}

@test "gate-check 02_assets is blocked when 01a_niche_analysis is locked" {
  run bash "$REPO/scripts/gate-check.sh" --stage 02_assets --project "$PROJECT"
  [ "$status" -ne 0 ]
  [[ "$output" == *"01a_niche_analysis"* ]] || [[ "$output" == *"not approved"* ]] || [[ "$output" == *"Niche analysis"* ]]
}

@test "gate-check 01a_niche_analysis fails when artifacts missing" {
  run bash "$REPO/scripts/gate-check.sh" --stage 01a_niche_analysis --project "$PROJECT"
  [ "$status" -ne 0 ]
}
```

- [ ] **Step 2: Run test to verify it fails initially (or passes — depends on whether earlier tasks already wired this in)**

Run: `bats tests/phase-niche/test-e2e-skip-prevention.bats`
Expected: tests pass if Tasks 2–3 are correct, fail otherwise.

- [ ] **Step 3: If failing, debug**

Most likely culprit: `gate-check.sh` doesn't yet handle the new stage key. Read `scripts/gate-check.sh` — usually it iterates through `stages.<key>` from yaml. If the test fails because of unknown stage, ensure stage-gates.yaml block from Task 3 is correct and gate-check has no hardcoded stage list.

If gate-check has hardcoded list (unlikely — Phase 3 made it data-driven), add 01a there too.

- [ ] **Step 4: Run all tests**

Run: `bats tests/phase-niche/`
Run: `python -m pytest tests/phase-niche/ -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/phase-niche/test-e2e-skip-prevention.bats
git commit -m "test(stage-01a): e2e skip-prevention covers new stage"
```

---

## Task 12: Backward compatibility для существующих проектов

**Files:**
- Modify: `scripts/gate-check.sh` (potentially)
- Create: `scripts/migrate-state-add-01a.sh`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Test scenario — existing project missing 01a key**

Add to `tests/phase-niche/test-e2e-skip-prevention.bats`:

```bash
@test "existing project without 01a key in state can be migrated" {
  REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  TMP="$(mktemp -d)"
  OLD="$TMP/old-project"
  mkdir -p "$OLD"
  # Simulate old state.yaml without 01a key
  cat > "$OLD/.landing-state.yaml" <<'EOF'
project: "old"
created: "2026-04-01T00:00:00Z"
schema_version: 1
stages:
  "00_brief":      {status: approved, timestamp: ""}
  "01_context":    {status: approved, timestamp: ""}
  "02_assets":     {status: approved, timestamp: ""}
  "03_references": {status: locked,   timestamp: ""}
EOF
  run bash "$REPO/scripts/migrate-state-add-01a.sh" "$OLD"
  [ "$status" -eq 0 ]
  grep -q "01a_niche_analysis" "$OLD/.landing-state.yaml"
  rm -rf "$TMP"
}
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Create scripts/migrate-state-add-01a.sh**

```bash
#!/usr/bin/env bash
# scripts/migrate-state-add-01a.sh
# Add 01a_niche_analysis stage to an existing project's .landing-state.yaml.
# If 02_assets is already approved, mark 01a as 'skipped' (legacy projects).
# Otherwise mark as 'locked'.
set -euo pipefail

PROJECT="${1:?usage: migrate-state-add-01a.sh <project-dir>}"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }

command -v yq >/dev/null 2>&1 || { echo "ERROR: yq required" >&2; exit 2; }

# Already migrated?
if yq -e '.stages."01a_niche_analysis"' "$STATE" >/dev/null 2>&1; then
    echo "Already has 01a_niche_analysis — no-op."
    exit 0
fi

# Decide initial status
assets_status="$(yq -r '.stages."02_assets".status // "locked"' "$STATE")"
if [ "$assets_status" = "approved" ]; then
    new_status="skipped"
    echo "02_assets already approved — marking 01a as 'skipped'."
else
    new_status="locked"
    echo "02_assets not yet approved — marking 01a as 'locked'."
fi

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
yq -i ".stages.\"01a_niche_analysis\" = {\"status\": \"$new_status\", \"timestamp\": \"$ts\"}" "$STATE"

echo "Migration done."
```

Make executable: `chmod +x scripts/migrate-state-add-01a.sh`

- [ ] **Step 4: Update gate-check.sh to recognize 'skipped' status**

Read `scripts/gate-check.sh`. The `all_approved` check in `gate-state.sh` currently treats any non-`approved` as missing. We need `skipped` to also count as «not blocking». Edit `scripts/gate-state.sh` — change the `all_approved` loop:

```bash
[ "$status" != "approved" ] && [ "$status" != "skipped" ] && missing+=("$s")
```

If existing tests fail because of this change, that's a real signal — investigate.

- [ ] **Step 5: Run tests to verify all pass**

Run: `bats tests/phase-niche/ tests/gate-check/`
Expected: all PASS, including pre-existing gate-check tests.

- [ ] **Step 6: Commit**

```bash
git add scripts/migrate-state-add-01a.sh scripts/gate-state.sh tests/phase-niche/test-e2e-skip-prevention.bats
git commit -m "feat(stage-01a): backward-compat migration script + skipped status"
```

---

## Task 13: package.json — npm script

**Files:**
- Modify: `package.json`

- [ ] **Step 1: Read package.json**

Run: `cat package.json`
Note pattern of existing test scripts (e.g. `test:phase-1`).

- [ ] **Step 2: Add test:phase-niche script**

Edit `package.json`, add to `scripts`:

```json
"test:phase-niche": "bats tests/phase-niche/ && python -m pytest tests/phase-niche/ -v"
```

- [ ] **Step 3: Run it**

Run: `npm run test:phase-niche`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add package.json
git commit -m "chore(stage-01a): npm test:phase-niche script"
```

---

## Task 14: Финальная проверка и push

- [ ] **Step 1: Run full test suite**

Run: `npm test`
Expected: all PASS, including new phase-niche tests.

- [ ] **Step 2: Manually verify gate-check on a fresh project**

```bash
bash scripts/gate-check.sh --stage 01a_niche_analysis --project /tmp/test-no-such-project 2>&1
```
Expected: meaningful error, not crash.

- [ ] **Step 3: Visual review of new stage tree**

Run: `ls template/01a_АНАЛИЗ_НИШИ/`
Expected: `.gitkeep`, `README.md`.

- [ ] **Step 4: Push branch**

```bash
git push origin main
```

---

## Self-Review

**1. Spec coverage check** (against [`docs/superpowers/specs/2026-05-06-niche-analysis-design.md`](../specs/2026-05-06-niche-analysis-design.md)):

- §1 «Цель» — Tasks 1, 5, 6 (template + agent + command)
- §1 «Принцип zero-touch» — Task 5 (agent file mentions это явно, тест проверяет)
- §1 «Язык артефактов» — Task 1 README + Task 5 agent
- §2 «Где встраивается» (01a между 01 и 02) — Task 2 (state) + Task 3 (gate dependency) + Task 8 (orchestrator)
- §3.1 niche-analysis.md формат — Task 1 README + Task 5 agent описывает структуру
- §3.2 competitors.yaml схема + 7 ролей + 15–25 — Task 4 validator + fixtures
- §3.2 confidence (high/medium/low) — Task 4 validator проверяет
- §3.3 positioning.md формат — Task 1 README + Task 5 agent
- §4.1 входы — Task 5 agent (00_БРИФ, 01_КОНТЕКСТ)
- §4.2 шаги алгоритма — Task 5 agent описание
- §4.3 tools — Task 5 agent
- §4.4 [ДОПУЩЕНИЕ] — Task 5 agent
- §5 контракты с downstream — Task 9
- §6.1 новые файлы — Tasks 1, 4, 5, 6, 7
- §6.2 модифицируемые файлы — Tasks 2, 3, 8, 9, 10, 13
- §6.3 backward compatibility — Task 12 (migration + skipped status)
- §7 acceptance criteria — Tasks 4 (validator), 5 (agent), 6 (command), 11 (e2e), 12 (legacy projects)

Все требования покрыты.

**2. Placeholder scan:** Проверил — нет TBD / TODO. Все code blocks полные. Команды конкретные.

Один потенциальный риск: Task 8 говорит «Insert a row/entry for 01a... adapt to actual structure». Это не placeholder, а необходимая адаптация под существующий формат файла, который агент-исполнитель прочитает в Step 1. Помечено явно.

**3. Type consistency:**
- Stage key `01a_niche_analysis` — везде одинаково (Tasks 2, 3, 4, 5, 6, 8, 11, 12)
- Folder `01a_АНАЛИЗ_НИШИ` — везде одинаково
- Artifact names: `niche-analysis.md`, `competitors.yaml`, `positioning.md` — везде одинаково
- 7 ролей — список идентичен в Task 4 fixtures, Task 5 agent, validator script
- `[ДОПУЩЕНИЕ]` (не `[ASSUMPTION]`) — везде

OK.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-06-niche-analysis-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — execute tasks in this session via executing-plans, batch with checkpoints.

Which approach?
