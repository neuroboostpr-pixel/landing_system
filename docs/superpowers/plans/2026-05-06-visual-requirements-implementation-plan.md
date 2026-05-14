# Visual Requirements Artifact Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить 4-й артефакт `visual-requirements.md` в этап `01a_АНАЛИЗ_НИШИ` со справочником `config/niche-visual-rules.yaml` (4 категории + default), чтобы данные о визуальном языке зашивались в pipeline и читались клиент-ассет-коллектором, мудбордом, references-curator и wp-builder.

**Architecture:** Справочник по категориям ниш + derive-логика из `competitors.yaml` в шаге 9 алгоритма `niche-analyst`. Артефакт — markdown со 7 секциями. Hard-check в gate-check на наличие файла. Backward-compat через существующий механизм `skipped`-статуса.

**Tech Stack:** YAML (справочник), Markdown (артефакт), bats (тесты структуры), pytest (валидатор), существующий `gate-check.sh`/`gate-state.sh`, агенты Claude Code (markdown frontmatter).

**Spec source:** [`docs/superpowers/specs/2026-05-06-visual-requirements-design.md`](../specs/2026-05-06-visual-requirements-design.md)

---

## File Structure

**Создаются:**
- `config/niche-visual-rules.yaml` — справочник по категориям ниш
- `tests/phase-niche/test-visual-rules.bats` — тесты структуры справочника
- `tests/phase-niche/test-validate-visual-requirements.py` — pytest для валидатора артефакта
- `tests/phase-niche/fixtures/visual-requirements-valid.md` — корректный пример артефакта
- `tests/phase-niche/fixtures/visual-requirements-missing-section.md` — фикстура с отсутствующей секцией
- `tests/phase-niche/fixtures/visual-requirements-too-few-flags.md` — фикстура с <3 ❌ или <3 ✅
- `skills/niche-analysis/scripts/validate-visual-requirements.py` — валидатор формата артефакта

**Модифицируются:**
- `agents/niche-analyst.md` — шаг 9 в алгоритме, обновление списка артефактов
- `agents/client-assets-collector.md` — Inputs from earlier stages с visual-requirements.md
- `agents/moodboard-composer.md` — расширение существующего блока Inputs
- `agents/references-curator.md` — расширение блока Inputs
- `agents/wp-builder.md` — новая секция Visual sanity-checks
- `config/stage-gates.yaml` — hard_check на visual-requirements.md
- `template/01a_АНАЛИЗ_НИШИ/README.md` — упомянуть 4-й артефакт
- `tests/phase-niche/test-niche-stage.bats` — новые тесты на наличие visual-requirements в требуемых артефактах и upon-the-rules

---

## Task 1: Справочник `config/niche-visual-rules.yaml`

**Files:**
- Create: `config/niche-visual-rules.yaml`
- Create: `tests/phase-niche/test-visual-rules.bats`

- [ ] **Step 1: Write failing bats tests**

Create `tests/phase-niche/test-visual-rules.bats`:

```bash
#!/usr/bin/env bats

setup() {
  RULES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/niche-visual-rules.yaml"
}

@test "niche-visual-rules.yaml exists" {
  [ -f "$RULES" ]
}

@test "niche-visual-rules.yaml is valid YAML" {
  python -c "import yaml; yaml.safe_load(open('$RULES', encoding='utf-8'))"
}

@test "rules has 4 MVP categories plus default" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$RULES', encoding='utf-8'))
required = {'premium_automotive', 'local_services', 'professional_services', 'b2c_consumer', 'default'}
got = set(d['categories'].keys())
assert required.issubset(got), f"missing: {required - got}"
EOF
}

@test "every category has minimum required fields" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$RULES', encoding='utf-8'))
required = {'description', 'hero_focal', 'hero_composition', 'photography',
            'people', 'product_treatment', 'background_allowed',
            'universal_red_flags', 'universal_preferences'}
for name, cat in d['categories'].items():
    missing = required - set(cat.keys())
    assert not missing, f"category {name} missing: {missing}"
EOF
}

@test "every category has at least 3 red flags and 3 preferences" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$RULES', encoding='utf-8'))
for name, cat in d['categories'].items():
    rf = cat.get('universal_red_flags', [])
    prefs = cat.get('universal_preferences', [])
    assert len(rf) >= 3, f"category {name}: only {len(rf)} red_flags"
    assert len(prefs) >= 3, f"category {name}: only {len(prefs)} preferences"
EOF
}

@test "schema_version is 1" {
  python -c "import yaml; d=yaml.safe_load(open('$RULES', encoding='utf-8')); assert d.get('schema_version') == 1"
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bats tests/phase-niche/test-visual-rules.bats`
Expected: 6 tests FAIL — file does not exist.

- [ ] **Step 3: Create config/niche-visual-rules.yaml**

```yaml
# Visual rules per niche category.
# Read by niche-analyst agent (step 9) to populate visual-requirements.md.
# Spec: docs/superpowers/specs/2026-05-06-visual-requirements-design.md

schema_version: 1

categories:
  premium_automotive:
    description: "Премиум-автодилеры (EV, гибриды, luxury ICE)"
    examples: ["BMW dealer", "Mercedes dealer", "Lixiang Dubai", "Tesla showroom"]
    hero_focal: product
    hero_composition: "Машина 50–70% кадра, фон — нейтральный или тёмный premium. Без городских пейзажей и driving shots."
    photography: studio
    people: optional
    people_note: "Если есть — family-интерьерные сцены, не sport-водительские"
    product_treatment: studio
    background_allowed:
      - studio_neutral
      - dark_premium
      - warm_interior
    universal_red_flags:
      - "Stock cityscape backgrounds (cheap dealer signal)"
      - "Highway driving shots (generic dealership template)"
      - "Off-road dramatic landscapes (Range Rover territory)"
      - "Sport-lifestyle shots (Tesla/Zeekr territory unless brand is sport-positioned)"
    universal_preferences:
      - "Studio shots с нейтральным или тёмным premium-фоном"
      - "Interior detail shots premium-материалов"
      - "Family moments внутри салона (если family-positioned brand)"

  local_services:
    description: "Локальные услуги: ремонт, бурение, монтаж, мастера"
    examples: ["бурение скважин", "ремонт квартир", "натяжные потолки", "клининг"]
    hero_focal: person_or_process
    hero_composition: "Реальный человек делает работу или готовый результат. Не stock-актёры."
    photography: documentary
    people: yes
    people_note: "Реальная команда клиента, а не stock smiling actors"
    product_treatment: context
    background_allowed:
      - real_workplace
      - finished_result
      - geo_local
    universal_red_flags:
      - "Stock smiling actors в касках (low trust signal)"
      - "Generic abstract icons в Hero вместо реальных людей/процесса"
      - "Tools/equipment вне контекста использования"
      - "Photoshop-составные коллажи"
    universal_preferences:
      - "Real team photos с лицами"
      - "Before/after или process shots"
      - "Geo-cues локального рынка (виды конкретного города/района)"

  professional_services:
    description: "Профессиональные услуги: медицина, право, консалтинг, образование"
    examples: ["частная стоматология", "адвокатский кабинет", "психолог", "репетитор-онлайн"]
    hero_focal: person_or_environment
    hero_composition: "Портрет эксперта или среда профессии. Trust signal на первом месте."
    photography: lifestyle_or_studio
    people: yes
    people_note: "Реальный эксперт/команда, не stock business meeting"
    product_treatment: hybrid
    background_allowed:
      - real_office
      - real_clinic
      - portrait_studio
      - documentary_moment
    universal_red_flags:
      - "Stock 'business meeting' photos"
      - "Generic handshakes"
      - "Suit-and-tie cliche shots"
      - "Stock medical actors (особенно для клиник)"
    universal_preferences:
      - "Real expert portraits с подписями (имя, регалии)"
      - "Environment, signaling competence (реальная клиника, реальный кабинет)"
      - "Documentary moments из работы"

  b2c_consumer:
    description: "B2C-товары: e-commerce, FMCG, товары через лендинги"
    examples: ["косметика DTC", "одежда", "электроника", "БАДы"]
    hero_focal: product_or_usage
    hero_composition: "Продукт в использовании или hero shot. Lifestyle-контекст допускается."
    photography: lifestyle_or_studio
    people: optional
    people_note: "Если есть — diverse, authentic, не stock-модели"
    product_treatment: context_or_studio
    background_allowed:
      - studio_neutral
      - lifestyle_context
      - in_use
    universal_red_flags:
      - "Pure abstract gradients без продукта"
      - "Mock UI с fake данными (для физических товаров)"
      - "Чрезмерно ретушированные модели"
    universal_preferences:
      - "Продукт в реальном использовании"
      - "Diverse, authentic модели если люди в кадре"
      - "Размер/масштаб продукта понятен"

  default:
    description: "Шаблон по умолчанию когда категория не определена"
    examples: []
    hero_focal: product_or_person
    hero_composition: "Понятный focal point. Без stock-подделок."
    photography: documentary_or_studio
    people: optional
    product_treatment: hybrid
    background_allowed:
      - studio_neutral
      - relevant_context
    universal_red_flags:
      - "Stock photos без relevance к нише"
      - "Generic abstract gradients вместо контента"
      - "Mismatch между обещанием и визуалом"
    universal_preferences:
      - "Authentic content над stock"
      - "Focal point должен быть понятен за 1 секунду"
      - "Соответствие обещанию из брифа"
```

- [ ] **Step 4: Run tests to verify all pass**

Run: `bats tests/phase-niche/test-visual-rules.bats`
Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```
git add config/niche-visual-rules.yaml tests/phase-niche/test-visual-rules.bats
git commit -m "$(cat <<'EOF'
feat(visual-rules): niche-visual-rules.yaml with 4 MVP categories

Plan task 1/9. Spec: docs/superpowers/specs/2026-05-06-visual-requirements-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Валидатор `validate-visual-requirements.py` + фикстуры

**Files:**
- Create: `skills/niche-analysis/scripts/validate-visual-requirements.py`
- Create: `tests/phase-niche/test-validate-visual-requirements.py`
- Create: `tests/phase-niche/fixtures/visual-requirements-valid.md`
- Create: `tests/phase-niche/fixtures/visual-requirements-missing-section.md`
- Create: `tests/phase-niche/fixtures/visual-requirements-too-few-flags.md`

- [ ] **Step 1: Create 3 fixture files**

`tests/phase-niche/fixtures/visual-requirements-valid.md` — корректный документ:

```markdown
# Визуальные требования: Test Brand

> Тип ниши: premium_automotive
> Тип бренда: 2
> Дата: 2026-05-06
> Источник: 00_БРИФ/brief.md, 01a_АНАЛИЗ_НИШИ/competitors.yaml

## 1. Hero focal point
**Что в центре первого экрана:** product
**Композиция:** Машина 50–70% кадра.

## 2. Photography style
studio. Категория диктует студийность.

## 3. People in frame
optional. Family-сцены допустимы.

## 4. Product treatment в каталоге/услугах
studio. Каждая модель на нейтральном фоне.

## 5. Background palette
**Допустимые:** studio_neutral, dark_premium
**Запрещённые:** cityscape, highway

## 6. Red flags для этой ниши
- ❌ Stock cityscape — сигнал cheap
- ❌ Sport lifestyle — поляна Tesla
- ❌ Off-road landscape — поляна Range Rover
- ✅ Studio shots
- ✅ Family interior moments
- ✅ Detail shots premium-материалов

## 7. Источники правил
- Справочник: config/niche-visual-rules.yaml → premium_automotive
- Derive из competitors.yaml: BMW iX (cool minimalism — избегаем).
```

`tests/phase-niche/fixtures/visual-requirements-missing-section.md` — отсутствует Section 6:

```markdown
# Визуальные требования: Test

## 1. Hero focal point
product

## 2. Photography style
studio

## 3. People in frame
no

## 4. Product treatment
studio

## 5. Background palette
neutral

## 7. Источники правил
default
```

`tests/phase-niche/fixtures/visual-requirements-too-few-flags.md` — Section 6 есть, но flags недостаточно:

```markdown
# Визуальные требования: Test

## 1. Hero focal point
product

## 2. Photography style
studio

## 3. People in frame
no

## 4. Product treatment
studio

## 5. Background palette
neutral

## 6. Red flags для этой ниши
- ❌ One bad thing
- ✅ One good thing

## 7. Источники правил
default
```

- [ ] **Step 2: Write failing pytest**

Create `tests/phase-niche/test-validate-visual-requirements.py`:

```python
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-visual-requirements.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("visual-requirements-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_missing_section_fails():
    r = run("visual-requirements-missing-section.md")
    assert r.returncode != 0
    assert "section" in (r.stdout + r.stderr).lower() or "6" in (r.stdout + r.stderr)


def test_too_few_flags_fails():
    r = run("visual-requirements-too-few-flags.md")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "3" in out or "minimum" in out or "least" in out
```

- [ ] **Step 3: Run pytest, verify 3 failures (script doesn't exist)**

Run: `python -m pytest tests/phase-niche/test-validate-visual-requirements.py -v`

- [ ] **Step 4: Implement validator**

Create `skills/niche-analysis/scripts/validate-visual-requirements.py`:

```python
#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/visual-requirements.md against schema.

Checks:
- All 7 sections present (## 1. ... ## 7.)
- Section 6 has at least 3 entries with ❌ and at least 3 with ✅
Exits 0 on valid, 1 on errors with messages on stdout.
"""
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    r"##\s*1\.\s*Hero\s+focal\s+point",
    r"##\s*2\.\s*Photography\s+style",
    r"##\s*3\.\s*People\s+in\s+frame",
    r"##\s*4\.\s*Product\s+treatment",
    r"##\s*5\.\s*Background\s+palette",
    r"##\s*6\.\s*Red\s+flags",
    r"##\s*7\.\s*Источники\s+правил",
]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    # Section presence
    for i, pattern in enumerate(REQUIRED_SECTIONS, start=1):
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"Section {i} missing or malformed (pattern: {pattern})")

    # Section 6 content: minimum 3 ❌ and 3 ✅
    s6_match = re.search(
        r"##\s*6\.\s*Red\s+flags.*?(?=##\s*7\.|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if s6_match:
        s6_text = s6_match.group(0)
        red = len(re.findall(r"^[\s-]*❌", s6_text, re.MULTILINE))
        green = len(re.findall(r"^[\s-]*✅", s6_text, re.MULTILINE))
        if red < 3:
            errors.append(f"Section 6: at least 3 red flags (❌) required, found {red}")
        if green < 3:
            errors.append(f"Section 6: at least 3 preferences (✅) required, found {green}")
    else:
        # Already reported via section presence; do not double-report

        pass

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-visual-requirements.py <visual-requirements.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("visual-requirements.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run pytest, verify all pass**

Run: `python -m pytest tests/phase-niche/test-validate-visual-requirements.py -v`
Expected: 3/3 PASS.

- [ ] **Step 6: Commit**

```
git add skills/niche-analysis/scripts/validate-visual-requirements.py tests/phase-niche/test-validate-visual-requirements.py tests/phase-niche/fixtures/visual-requirements-*.md
git commit -m "$(cat <<'EOF'
feat(visual-requirements): markdown validator + fixtures

Plan task 2/9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Расширить `niche-analyst.md` — шаг 9

**Files:**
- Modify: `agents/niche-analyst.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing bats tests**

Append to `tests/phase-niche/test-niche-stage.bats`:

```bash
@test "niche-analyst documents step 9 visual requirements" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "visual-requirements.md\|niche-visual-rules.yaml" "$AGENT"
}

@test "niche-analyst lists visual-requirements.md in outputs" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "visual-requirements.md" "$AGENT"
}
```

- [ ] **Step 2: Run tests, verify 2 new failures**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: previously-passing tests still PASS, 2 new FAIL.

- [ ] **Step 3: Edit `agents/niche-analyst.md`**

Read it first. Find the Outputs section (`## Выходы`) and add a 4-th item:

```markdown
4. `visual-requirements.md` — визуальные требования к лендингу: hero focal, photography style, product treatment, background palette, red flags. Структура и валидатор: `skills/niche-analysis/scripts/validate-visual-requirements.py`. Справочник по категориям: `config/niche-visual-rules.yaml`.
```

Find the algorithm section (`## Алгоритм`) and append a new step after step 8 (the validator step):

```markdown
9. **Визуальные требования.**
   1. **Классификация категории:** на основе бренда/продукта/категории из брифа сопоставить с `categories[].examples` в `config/niche-visual-rules.yaml`. Если совпадение явное (Lixiang Dubai → premium_automotive) — берём `category_key`. Если неоднозначное — выбираем по доминирующему сигналу. Если нет совпадения — `category_key = default` + пометка `[ДОПУЩЕНИЕ] категория не в справочнике`.
   2. **Базовые правила:** скопировать из `categories[category_key]`: `hero_focal`, `hero_composition`, `photography`, `people`, `product_treatment`, `background_allowed`, `universal_red_flags`, `universal_preferences`.
   3. **Derive из конкурентов:** прочитать `competitors.yaml`, поле `visual_notes` каждой записи. Для `role=direct` и `role=local_competitor` найти повторяющиеся визуальные коды (≥2 конкурента упоминают похожее) → добавить в red_flags «занятая поляна <имя>». Найти gaps → добавить в preferences. Для `role=manufacturer` и `role=local_dealer` отметить визуальные коды как «наследовать» в preferences.
   4. **Запись `visual-requirements.md`** с 7 секциями (см. `skills/niche-analysis/scripts/validate-visual-requirements.py`).
   5. **Sanity-check:** Section 6 должна содержать минимум 3 ❌ и 3 ✅, каждый ❌ — с обоснованием (категорийное правило или ссылка на конкурента).
   6. **Валидация:** запустить `python skills/niche-analysis/scripts/validate-visual-requirements.py 01a_АНАЛИЗ_НИШИ/visual-requirements.md`. Если errors — исправить и повторить.
```

Renumber existing step 9 (если был) → 10. (Из существующего файла — там уже шаг 8 «Самопроверка» через validate-competitors.py; новый шаг становится 9, дальнейших не было.)

- [ ] **Step 4: Run tests, verify all pass**

Run: `bats tests/phase-niche/test-niche-stage.bats`
Expected: all PASS including 2 new ones.

- [ ] **Step 5: Commit**

```
git add agents/niche-analyst.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(niche-analyst): step 9 — visual requirements artifact

Plan task 3/9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: stage-gates.yaml — hard_check для visual-requirements.md

**Files:**
- Modify: `config/stage-gates.yaml`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing bats test**

```bash
@test "stage-gates 01a includes visual_requirements_md hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "visual_requirements_md\|visual-requirements.md" "$GATES"
}
```

- [ ] **Step 2: Run tests, verify 1 new failure**

`bats tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 3: Edit config/stage-gates.yaml**

In the `01a_niche_analysis` block, in `hard_checks` array (after `competitors_schema`), insert one more check entry:

```yaml
      - id: visual_requirements_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/visual-requirements.md"
        required: true
        fix_hint: "niche-analyst agent creates this (step 9)"
      - id: visual_requirements_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-visual-requirements.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/visual-requirements.md"]
        required: true
        fix_hint: "Fix visual-requirements.md sections — see script output"
```

- [ ] **Step 4: Run tests + validate yaml**

```
bats tests/phase-niche/test-niche-stage.bats
python -c "import yaml; yaml.safe_load(open('config/stage-gates.yaml', encoding='utf-8'))"
```
Expected: tests PASS, YAML exit 0.

- [ ] **Step 5: Commit**

```
git add config/stage-gates.yaml tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(stage-gates): require visual-requirements.md in stage 01a

Plan task 4/9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Контракты с downstream-агентами

**Files:**
- Modify: `agents/client-assets-collector.md`
- Modify: `agents/moodboard-composer.md`
- Modify: `agents/references-curator.md`
- Modify: `agents/wp-builder.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing bats tests**

```bash
@test "client-assets-collector reads visual-requirements.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/client-assets-collector.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "moodboard-composer reads visual-requirements.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/moodboard-composer.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "references-curator reads visual-requirements.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/references-curator.md"
  grep -q "visual-requirements.md" "$AGENT"
}

@test "wp-builder has visual sanity-checks section" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/wp-builder.md"
  grep -q "visual-requirements.md\|Visual sanity" "$AGENT"
}
```

- [ ] **Step 2: Run tests, verify 4 failures**

`bats tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 3: Update each agent**

For `agents/client-assets-collector.md` — append at the end:

```markdown

## Inputs from earlier stages

- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — обязательный input. Sections 1, 2, 3, 4, 6 определяют, какие фото запрашивать у клиента и каких фото запрашивать НЕ нужно. Перед запросом материалов клиенту прочитать red flags (Section 6) и явно указать в брифе, что не подходит.
```

For `agents/moodboard-composer.md` — find existing «Inputs from earlier stages» block (added previously for niche-analysis.md) and append below:

```markdown
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — обязательный input. Sections 1, 2, 3, 5, 6 определяют визуальный язык референсов. Если referенс попадает в red flag (Section 6) — не сохранять.
```

For `agents/references-curator.md` — find existing «Inputs from earlier stages» block (added previously) and append below:

```markdown
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — Section 6 (red flags) обязательна к проверке. При оценке любого референса (от пользователя или moodboard-composer) сравнивать с red flags. Референсы, попадающие в запреты, отвергать со ссылкой на конкретный пункт visual-requirements.md.
```

For `agents/wp-builder.md` — append at the end:

```markdown

## Visual sanity-checks

Перед сборкой темы и финальной упаковкой ассетов:

1. **Прочитать `01a_АНАЛИЗ_НИШИ/visual-requirements.md`** (Sections 1, 4, 5).
2. **Hero asset check:** если Section 1 говорит `hero_focal: product`, проверить главный hero-кандидат в `02_МАТЕРИАЛЫ_КЛИЕНТА/`. Если имя файла или метаданные содержат паттерны из Section 5 «Запрещённые» (например, `cityscape`, `landscape`, `highway`) — warning в build log, рекомендовать замену.
3. **Catalog assets check:** если Section 4 говорит `studio`, проверить файлы моделей. Файлы с landscape-фоном — warning.
4. **Запрет fallback на stock:** в коде темы (`block-hero.php`, `block-models.php` и т.д.) запрещены fallback-картинки на сторонние URL (Pexels, Unsplash и т.п.) без явного разрешения в visual-requirements. Если fallback нужен — должен быть локальный файл, проверенный против Section 5.
5. **Code review:** grep по теме на признаки запрещённых паттернов (например, имена файлов `*-stock-*`, `*-pexels-*`).
```

- [ ] **Step 4: Run tests, verify all pass**

`bats tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 5: Commit**

```
git add agents/client-assets-collector.md agents/moodboard-composer.md agents/references-curator.md agents/wp-builder.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(visual-requirements): downstream agents (02/03/08) read visual-requirements.md

Plan task 5/9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Update template README

**Files:**
- Modify: `template/01a_АНАЛИЗ_НИШИ/README.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing bats test**

```bash
@test "template 01a README mentions visual-requirements.md" {
  README="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template/01a_АНАЛИЗ_НИШИ" && pwd)/README.md"
  grep -q "visual-requirements.md" "$README"
}
```

- [ ] **Step 2: Run tests, verify 1 failure**

- [ ] **Step 3: Edit `template/01a_АНАЛИЗ_НИШИ/README.md`**

Find the `## Артефакты` section. Add a 4-th item:

```markdown
- `visual-requirements.md` — визуальные требования: hero focal point, photography style, product treatment, фоны, red flags для конкретной ниши. Источник правил: `config/niche-visual-rules.yaml` + derive из competitors.yaml.
```

Also update «Что читает после» section, append:

```markdown
- `client-assets-collector` (этап 02) — `visual-requirements.md`
- `wp-builder` (этап 08) — `visual-requirements.md` (sanity-checks)
```

- [ ] **Step 4: Run tests, verify all pass**

- [ ] **Step 5: Commit**

```
git add template/01a_АНАЛИЗ_НИШИ/README.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
docs(stage-01a): document visual-requirements.md in template README

Plan task 6/9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: E2E test — gate-check блокирует stage 01a без visual-requirements

**Files:**
- Modify: `tests/phase-niche/test-e2e-skip-prevention.bats`

- [ ] **Step 1: Append failing bats test**

Append to `tests/phase-niche/test-e2e-skip-prevention.bats`:

```bash
@test "gate-check 01a fails when visual-requirements.md is missing (other 3 artifacts present)" {
  REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  TMP="$BATS_TEST_TMPDIR"
  PROJECT="$TMP/test-vr-missing"
  mkdir -p "$PROJECT"
  cp -r "$REPO/template/." "$PROJECT/"
  if command -v yq >/dev/null 2>&1; then
    yq -i '.stages."00_brief".status = "approved"' "$PROJECT/.landing-state.yaml"
  else
    skip "yq not installed"
  fi
  # Provide 3 of 4 artifacts; visual-requirements.md missing
  mkdir -p "$PROJECT/01a_АНАЛИЗ_НИШИ"
  printf "# stub\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/niche-analysis.md"
  printf "competitors: []\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/competitors.yaml"
  printf "# stub\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md"

  run bash "$REPO/scripts/gate-check.sh" --stage 01a_niche_analysis --project "$PROJECT" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"visual-requirements"* ]] || [[ "$output" == *"visual_requirements_md"* ]]
}
```

- [ ] **Step 2: Run e2e tests**

`bats tests/phase-niche/test-e2e-skip-prevention.bats`
Expected: previously-passing tests still PASS, the new one PASSES too because gate-check.sh already supports type=file_exists and the new hard_check from Task 4 is registered. If FAIL — check that Task 4 was correctly applied to stage-gates.yaml.

(This test is essentially a regression check — it doesn't require new implementation, since Tasks 1–4 already wired everything in. If it fails, it indicates a wiring bug from those tasks.)

- [ ] **Step 3: Commit**

```
git add tests/phase-niche/test-e2e-skip-prevention.bats
git commit -m "$(cat <<'EOF'
test(visual-requirements): e2e — gate-check blocks 01a without visual-requirements.md

Plan task 7/9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Manual smoke test — generate visual-requirements.md for lixiang-dubai

This is a manual verification step (not a code change) to prove the pipeline works end-to-end on a real project. The user-facing benefit of this artefact is shown by writing one for `lixiang-dubai` and confirming `gate-check` passes.

**Files:**
- Create: `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/visual-requirements.md` (manually, mirroring the spec example)

- [ ] **Step 1: Generate visual-requirements.md for lixiang-dubai**

Use the example block from spec §2 «Пример (lixiang-dubai)» as the content. Save to `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/visual-requirements.md`.

- [ ] **Step 2: Run validator**

```
python skills/niche-analysis/scripts/validate-visual-requirements.py /d/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/visual-requirements.md
```
Expected: exit 0, "OK: ... is valid".

- [ ] **Step 3: Run gate-check on the project**

```
bash scripts/gate-check.sh --stage 01a_niche_analysis --project /d/AI_TEAMS/Lendings/lixiang-dubai --auto
```
Expected: all 5 hard_checks (existing 4 + new visual_requirements_md + visual_requirements_schema) green.

- [ ] **Step 4: No commit needed (lixiang-dubai is not part of the system repo)**

The manual artefact lives in the lixiang-dubai project folder, which is a separate concern from the landing_system repo.

---

## Task 9: Финальная валидация и push

- [ ] **Step 1: Run full test suite**

```
npm test
npm run test:phase-niche
```
Expected: all PASS.

- [ ] **Step 2: Verify spec coverage**

Re-read the spec acceptance criteria (§8). Ensure each is met:
- 4 артефакта в `01a_АНАЛИЗ_НИШИ/` после `/landing-niche` — yes, niche-analyst now creates 4
- 7 секций в visual-requirements.md — validated by validator
- Section 6: 3+ ❌ and 3+ ✅ — validated
- Категория из справочника — Tasks 1, 3
- Default + ДОПУЩЕНИЕ если нет совпадения — Task 3 algorithm
- Минимум 1 red flag со ссылкой на конкурента — Task 3 algorithm step 9.3
- gate-check passes only when all 5+ hard_checks green — Task 4
- Existing проекты не падают через `skipped` — preserved from previous spec
- Bats-тесты на справочник — Task 1

- [ ] **Step 3: Push**

```
git push origin main
```

---

## Self-Review

**1. Spec coverage:**

- §1 Цель + Принцип → Task 3 (agent step 9)
- §2 Структура артефакта → Task 2 (validator), Task 8 (manual smoke)
- §3 Справочник категорий → Task 1
- §4 Алгоритм агента → Task 3
- §5 Контракты с downstream-агентами + gate-check → Tasks 4, 5
- §6 Backward compat → preserved (no new code, uses existing `skipped` mechanism)
- §7 Файлы — covered across tasks
- §8 Acceptance criteria → Task 9 step 2

All §1–§8 covered.

**2. Placeholder scan:** прошёл — нет TBD/TODO. Каждый шаг содержит actual content.

**3. Type consistency:**
- `visual-requirements.md` — везде одинаково
- `niche-visual-rules.yaml` — везде
- `category_key` — единый термин
- 7 sections — везде согласовано
- 3+ ❌ / 3+ ✅ — Tasks 1 (rules), 2 (validator), spec §2

OK.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-06-visual-requirements-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks.

**2. Inline Execution** — execute tasks in this session via executing-plans, batch with checkpoints.

Which approach?
