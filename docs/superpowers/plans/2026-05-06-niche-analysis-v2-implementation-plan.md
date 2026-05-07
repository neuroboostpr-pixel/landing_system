# Niche Analysis v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать v2 этапа `01a_АНАЛИЗ_НИШИ`: справочник режимов позиционирования + 2 новых артефакта (`market-profile.md`, `landing-structure.md`) + 3 шаблона `positioning.md` (rational / emotional_aspiration / trust_authority) + классификация режима в `niche-analyst` + миграция legacy-проектов через stub.

**Architecture:** Расширение существующего pipeline 01a без слома backward-compat. Новые артефакты живут рядом со старыми, агент `niche-analyst` получает 3 новых шага (4, 7, 9). Контракты с downstream обновляются. Миграция legacy через stub-генератор. Реализуется поэтапно: справочник → артефакты → агент → контракты → миграция → smoke на lixiang.

**Tech Stack:** YAML (справочник режимов), Markdown (3 шаблона + 2 новых артефакта), Python (3 новых валидатора + миграционный скрипт), bats (структурные тесты), pytest (тесты валидаторов), существующий gate-check pipeline.

**Spec source:** [`docs/superpowers/specs/2026-05-06-niche-analysis-v2-design.md`](../specs/2026-05-06-niche-analysis-v2-design.md)

---

## Phases

План разбит на 6 фаз, каждая фаза — связанный кусок работы:

| Phase | Tasks | Что делается |
|---|---|---|
| **A. Foundation** | 1–3 | Справочник `positioning-modes.yaml` + расширение `niche-visual-rules.yaml` |
| **B. Validators & artifacts** | 4–9 | 3 новых валидатора + 3 шаблона positioning + 2 новых артефакта |
| **C. Agent integration** | 10–12 | Расширение `niche-analyst.md` алгоритмом 12 шагов |
| **D. Downstream contracts** | 13–15 | brand-architect, content-writer, wp-builder читают новые артефакты |
| **E. Gate-check & docs** | 16–18 | stage-gates 4 новых hard_check + template README + main README |
| **F. Migration & smoke** | 19–22 | migrate-niche-to-v2 + lixiang smoke + push |

---

## File Structure

**Создаются (новые файлы):**
- `config/positioning-modes.yaml` — справочник режимов и матрица
- `skills/niche-analysis/scripts/validate-market-profile.py` — валидатор market-profile.md
- `skills/niche-analysis/scripts/validate-positioning.py` — валидатор positioning.md (mode-aware)
- `skills/niche-analysis/scripts/validate-landing-structure.py` — валидатор landing-structure.md
- `scripts/migrate-niche-to-v2.sh` — миграция legacy v1 проектов через stub
- `tests/phase-niche/test-positioning-modes.bats` — тесты справочника
- `tests/phase-niche/test-validate-market-profile.py` — pytest для market-profile валидатора
- `tests/phase-niche/test-validate-positioning.py` — pytest для mode-aware валидатора
- `tests/phase-niche/test-validate-landing-structure.py` — pytest для landing-structure валидатора
- `tests/phase-niche/test-migrate-niche-to-v2.bats` — bats для миграции
- `tests/phase-niche/fixtures/market-profile-valid.md`
- `tests/phase-niche/fixtures/market-profile-missing-tier.md`
- `tests/phase-niche/fixtures/positioning-rational-valid.md`
- `tests/phase-niche/fixtures/positioning-emotional-valid.md`
- `tests/phase-niche/fixtures/positioning-trust-valid.md`
- `tests/phase-niche/fixtures/positioning-no-mode-header.md`
- `tests/phase-niche/fixtures/positioning-mode-template-mismatch.md`
- `tests/phase-niche/fixtures/landing-structure-valid.md`
- `tests/phase-niche/fixtures/landing-structure-missing-hero.md`

**Модифицируемые:**
- `agents/niche-analyst.md` — расширяется до 12 шагов
- `agents/brand-architect.md` — читает market-profile + landing-structure
- `agents/content-writer.md` — читает landing-structure, распознаёт mode
- `agents/wp-builder.md` — генерирует темы по landing-structure
- `config/stage-gates.yaml` — 4 новых hard_check для 01a
- `config/niche-visual-rules.yaml` — добавление маркеров режима в категории (минимальное)
- `template/01a_АНАЛИЗ_НИШИ/README.md` — упоминание 6 артефактов
- `tests/phase-niche/test-niche-stage.bats` — новые проверки структуры
- `README.md` — короткое упоминание v2

---

# Phase A: Foundation

## Task 1: Справочник `config/positioning-modes.yaml`

**Files:**
- Create: `config/positioning-modes.yaml`
- Create: `tests/phase-niche/test-positioning-modes.bats`

- [ ] **Step 1: Write failing bats tests**

Create `tests/phase-niche/test-positioning-modes.bats`:

```bash
#!/usr/bin/env bats

setup() {
  RULES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/positioning-modes.yaml"
  PY_RULES="$(cygpath -m "$RULES" 2>/dev/null || echo "$RULES" | sed 's|^/\([a-z]\)/|\1:/|')"
}

@test "positioning-modes.yaml exists" {
  [ -f "$RULES" ]
}

@test "positioning-modes.yaml is valid YAML" {
  python -c "import yaml; yaml.safe_load(open('$PY_RULES', encoding='utf-8'))"
}

@test "schema_version is 1" {
  python -c "import yaml; d=yaml.safe_load(open('$PY_RULES', encoding='utf-8')); assert d.get('schema_version') == 1"
}

@test "all 3 modes defined: rational, emotional_aspiration, trust_authority" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
required = {'rational', 'emotional_aspiration', 'trust_authority'}
got = set(d['modes'].keys())
assert required.issubset(got), f"missing modes: {required - got}"
EOF
}

@test "every mode has template_sections (min 4) and typical_categories" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
for name, mode in d['modes'].items():
    assert 'template_sections' in mode, f"{name}: missing template_sections"
    assert len(mode['template_sections']) >= 4, f"{name}: only {len(mode['template_sections'])} sections"
    assert 'typical_categories' in mode, f"{name}: missing typical_categories"
EOF
}

@test "mode_prediction_matrix has at least 5 rules" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
m = d.get('mode_prediction_matrix', [])
assert len(m) >= 5, f"need >=5 rules, got {len(m)}"
EOF
}

@test "brief_indicators has all 3 modes" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
ind = d.get('brief_indicators', {})
assert {'rational', 'emotional_aspiration', 'trust_authority'}.issubset(ind.keys())
for name, words in ind.items():
    assert len(words) >= 5, f"{name}: only {len(words)} indicator words"
EOF
}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `bats tests/phase-niche/test-positioning-modes.bats`
Expected: 7 tests FAIL — file does not exist.

- [ ] **Step 3: Create `config/positioning-modes.yaml`**

```yaml
# Positioning modes registry + selection matrix.
# Read by niche-analyst (step 7) to classify positioning mode.
# Spec: docs/superpowers/specs/2026-05-06-niche-analysis-v2-design.md §10

schema_version: 1

modes:
  rational:
    description: "Продажа через функциональный benefit, метрики, ROI"
    template_sections:
      - "Job statement"
      - "Desired outcomes"
      - "Metrics that matter"
      - "Functional benefit ladder"
      - "Чего избегать"
    typical_categories:
      - "b2b_saas"
      - "utility_services"
      - "tools"
      - "commodity"

  emotional_aspiration:
    description: "Продажа через статус, эмоцию, identity"
    template_sections:
      - "Character"
      - "Problem"
      - "Guide"
      - "Plan"
      - "Call to Action"
      - "Success vision"
      - "Failure vision"
      - "Tone of voice"
      - "Чего избегать"
    typical_categories:
      - "luxury"
      - "premium_consumer"
      - "lifestyle"
      - "fashion"
      - "premium_automotive"

  trust_authority:
    description: "Продажа через доверие и снятие риска"
    template_sections:
      - "Authority signals"
      - "Process transparency"
      - "Social proof tiers"
      - "Risk reversal"
      - "Чего избегать"
    typical_categories:
      - "medical"
      - "legal"
      - "financial"
      - "premium_services"
      - "local_services_high_trust"

mode_prediction_matrix:
  - if:
      accessibility_tier: ["utility_essential", "mass_consumer"]
      regulated: false
    predict: "rational"

  - if:
      accessibility_tier: ["mass_consumer", "mid_premium"]
      regulated: true
    predict: "trust_authority"

  - if:
      accessibility_tier: ["mid_premium"]
      emotional_load: "high"
    predict: "hybrid:emotional_aspiration+trust_authority"

  - if:
      accessibility_tier: ["premium", "luxury_status", "ultra_luxury"]
      regulated: false
    predict: "emotional_aspiration"

  - if:
      accessibility_tier: ["premium"]
      regulated: true
    predict: "hybrid:trust_authority+emotional_aspiration"

  - if:
      accessibility_tier: ["luxury_status", "ultra_luxury"]
      regulated: true
    predict: "hybrid:emotional_aspiration+trust_authority"

brief_indicators:
  rational:
    - "экономия"
    - "гарантия"
    - "дешевле"
    - "KPI"
    - "срок"
    - "ROI"
    - "эффективность"
    - "fixed price"
    - "transparent"
  emotional_aspiration:
    - "премиум"
    - "эксклюзив"
    - "статус"
    - "династия"
    - "безупречный"
    - "culture"
    - "lifestyle"
    - "luxury"
  trust_authority:
    - "сертификат"
    - "опыт"
    - "отзывы"
    - "лицензия"
    - "врач"
    - "лет на рынке"
    - "клиника"
    - "credentials"
```

- [ ] **Step 4: Run tests to verify all pass**

Run: `bats tests/phase-niche/test-positioning-modes.bats`
Expected: 7/7 PASS.

- [ ] **Step 5: Commit**

```
git add config/positioning-modes.yaml tests/phase-niche/test-positioning-modes.bats
git commit -m "$(cat <<'EOF'
feat(positioning-modes): registry of 3 modes + prediction matrix

Plan task 1/22. Spec: docs/superpowers/specs/2026-05-06-niche-analysis-v2-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Расширить `niche-visual-rules.yaml` с маркерами режима

**Files:**
- Modify: `config/niche-visual-rules.yaml`
- Modify: `tests/phase-niche/test-visual-rules.bats`

- [ ] **Step 1: Append failing test**

```bash
@test "every category has default_positioning_mode" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
valid_modes = {'rational', 'emotional_aspiration', 'trust_authority',
               'hybrid:emotional_aspiration+trust_authority',
               'hybrid:trust_authority+emotional_aspiration',
               'hybrid:emotional_aspiration+rational',
               'hybrid:trust_authority+rational'}
for name, cat in d['categories'].items():
    mode = cat.get('default_positioning_mode')
    assert mode is not None, f"{name}: no default_positioning_mode"
    assert mode in valid_modes, f"{name}: invalid mode '{mode}'"
EOF
}
```

- [ ] **Step 2: Run tests to verify failure**

Run: `bats tests/phase-niche/test-visual-rules.bats`
Expected: this new test FAILs (existing 6 pass).

- [ ] **Step 3: Add `default_positioning_mode` to each category**

Edit `config/niche-visual-rules.yaml`. For each of 5 categories add field after `description`:

For `premium_automotive`:
```yaml
    default_positioning_mode: "emotional_aspiration"
```

For `local_services`:
```yaml
    default_positioning_mode: "trust_authority"
```

For `professional_services`:
```yaml
    default_positioning_mode: "trust_authority"
```

For `b2c_consumer`:
```yaml
    default_positioning_mode: "hybrid:emotional_aspiration+rational"
```

For `default`:
```yaml
    default_positioning_mode: "trust_authority"
```

- [ ] **Step 4: Verify all visual-rules tests still pass**

Run: `bats tests/phase-niche/test-visual-rules.bats`
Expected: 7/7 PASS (6 existing + 1 new).

- [ ] **Step 5: Commit**

```
git add config/niche-visual-rules.yaml tests/phase-niche/test-visual-rules.bats
git commit -m "$(cat <<'EOF'
feat(niche-visual-rules): default_positioning_mode per category

Plan task 2/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Тесты предиктора режима (sanity check матрицы)

**Files:**
- Modify: `tests/phase-niche/test-positioning-modes.bats`

Это task для проверки, что матрица предсказания корректна логически — тесты просто читают матрицу и проверяют, что для известных кейсов предсказание соответствует ожиданию.

- [ ] **Step 1: Append assertions**

```bash
@test "matrix predicts emotional_aspiration for premium tier non-regulated" {
  python <<EOF
import yaml
d = yaml.safe_load(open('$PY_RULES', encoding='utf-8'))
matrix = d['mode_prediction_matrix']

def predict(tier, regulated, emotional_load=None):
    for rule in matrix:
        cond = rule['if']
        if tier not in cond.get('accessibility_tier', []):
            continue
        if 'regulated' in cond and cond['regulated'] != regulated:
            continue
        if 'emotional_load' in cond and cond['emotional_load'] != emotional_load:
            continue
        return rule['predict']
    return None

# Premium auto in Dubai = premium tier, not regulated → emotional_aspiration
assert predict('premium', False) == 'emotional_aspiration'
# Drilling well = utility_essential, not regulated → rational
assert predict('utility_essential', False) == 'rational'
# Private clinic = mid_premium, regulated, high emotional → hybrid
assert predict('mid_premium', True) == 'trust_authority'
EOF
}
```

- [ ] **Step 2: Run tests, expect pass (matrix already correct from Task 1)**

Run: `bats tests/phase-niche/test-positioning-modes.bats`
Expected: all 8 tests PASS (7 existing + 1 new).

- [ ] **Step 3: Commit**

```
git add tests/phase-niche/test-positioning-modes.bats
git commit -m "$(cat <<'EOF'
test(positioning-modes): matrix prediction sanity checks

Plan task 3/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# Phase B: Validators & artifacts

## Task 4: Валидатор `validate-market-profile.py` + фикстуры

**Files:**
- Create: `skills/niche-analysis/scripts/validate-market-profile.py`
- Create: `tests/phase-niche/test-validate-market-profile.py`
- Create: `tests/phase-niche/fixtures/market-profile-valid.md`
- Create: `tests/phase-niche/fixtures/market-profile-missing-tier.md`

- [ ] **Step 1: Create valid fixture**

`tests/phase-niche/fixtures/market-profile-valid.md`:

```markdown
# Рыночный профиль: Test Brand

> Дата: 2026-05-06
> Регион: Дубай, ОАЭ

## 1. Accessibility tier
**Tier:** premium

**Обоснование:**
- Цена клиента/категории: AED 250 000
- Медианный доход региона: AED 25 000 / месяц (источник: https://example.com)
- Соотношение: 10 месячных доходов
- Сравнение с медианной ценой в категории: 1.2×

**Что это значит для позиционирования:** Премиум-покупка, доминирует emotional режим.

## 2. Consideration cycle
**Тип:** long

**Обоснование:** Семейная покупка авто — 1–4 месяца от первого касания до решения.

**Что это значит:** Глубокий нарратив, brand story нужен.

## 3. Decision unit
**Тип:** family

**Обоснование:** Решение принимается семьёй с consensus.

**Что это значит:** Family-first tone, акценты на детях/комфорте.

## 4. Regulated category
**Регулируется:** no

**Что это значит:** Trust-сигналы желательны, но не обязательны.

## 5. Emotional load
**Уровень:** medium

**Обоснование:** Семейное авто — внутренний уровень problem (хочу, чтобы семья гордилась).

**Что это значит:** Internal-уровень StoryBrand-проблемы.

## 6. Cultural context
**Регион:** Дубай, ОАЭ
**Ключевые культурные особенности рынка:**
- Открытая культура статуса
- Премиум через визуальную демонстрацию
- Экспат-аудитория (английский язык лендинга)

**Что это значит:** Можно открыто давить на статус.

## 7. Сводная рекомендация режима
**Predicted mode:** emotional_aspiration

## 8. Источники и допущения
- Median income: https://example.com/income
- [ДОПУЩЕНИЕ] Точная цена клиента не подтверждена брифом.
```

- [ ] **Step 2: Create invalid fixture (missing accessibility_tier)**

`tests/phase-niche/fixtures/market-profile-missing-tier.md`:

```markdown
# Рыночный профиль: Test

## 2. Consideration cycle
medium

## 3. Decision unit
individual

## 4. Regulated category
no

## 5. Emotional load
low

## 6. Cultural context
generic

## 7. Сводная рекомендация режима
**Predicted mode:** rational

## 8. Источники и допущения
none
```

(Section 1 missing → must fail.)

- [ ] **Step 3: Write failing pytest**

`tests/phase-niche/test-validate-market-profile.py`:

```python
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-market-profile.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("market-profile-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_missing_tier_fails():
    r = run("market-profile-missing-tier.md")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "tier" in out or "section 1" in out or "accessibility" in out
```

- [ ] **Step 4: Run pytest, expect 2 failures (script doesn't exist)**

Run: `python -m pytest tests/phase-niche/test-validate-market-profile.py -v`

- [ ] **Step 5: Implement validator**

`skills/niche-analysis/scripts/validate-market-profile.py`:

```python
#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/market-profile.md against schema.

Checks:
- All 8 sections present (## 1. ... ## 8.)
- Section 1 contains valid accessibility_tier value
- Section 7 contains valid Predicted mode value

Exits 0 on valid, 1 on errors with messages on stdout.
"""
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    (r"##\s*1\.\s*Accessibility\s+tier", 1),
    (r"##\s*2\.\s*Consideration\s+cycle", 2),
    (r"##\s*3\.\s*Decision\s+unit", 3),
    (r"##\s*4\.\s*Regulated\s+category", 4),
    (r"##\s*5\.\s*Emotional\s+load", 5),
    (r"##\s*6\.\s*Cultural\s+context", 6),
    (r"##\s*7\.\s*Сводная\s+рекомендация\s+режима", 7),
    (r"##\s*8\.\s*Источники\s+и\s+допущения", 8),
]

VALID_TIERS = {
    "utility_essential", "mass_consumer", "mid_premium",
    "premium", "luxury_status", "ultra_luxury",
}

VALID_CYCLES = {"impulse", "short", "medium", "long", "very_long"}
VALID_DECISION_UNITS = {"individual", "family", "corporate"}
VALID_EMOTIONAL_LOADS = {"low", "medium", "high"}
VALID_REGULATED = {"yes", "no"}

VALID_MODES_PATTERN = re.compile(
    r"^(rational|emotional_aspiration|trust_authority|hybrid:[a-z_]+\+[a-z_]+|legacy_v1)$"
)


def validate(path):
    errors = []
    text = path.read_text(encoding="utf-8")

    # 1. Sections
    for pattern, num in REQUIRED_SECTIONS:
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"Section {num} missing or malformed")

    # 2. Accessibility tier value
    tier_match = re.search(r"\*\*Tier:\*\*\s*([a-z_]+)", text, re.IGNORECASE)
    if tier_match:
        tier = tier_match.group(1).strip().lower()
        if tier not in VALID_TIERS:
            errors.append(f"Invalid accessibility tier: '{tier}'. Valid: {sorted(VALID_TIERS)}")
    else:
        # Already reported via section presence

        pass

    # 3. Predicted mode value
    mode_match = re.search(r"\*\*Predicted mode:\*\*\s*([a-z_+:]+)", text, re.IGNORECASE)
    if mode_match:
        mode = mode_match.group(1).strip().lower()
        if not VALID_MODES_PATTERN.match(mode):
            errors.append(
                f"Invalid Predicted mode: '{mode}'. Valid forms: rational | emotional_aspiration | trust_authority | hybrid:X+Y"
            )

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate-market-profile.py <market-profile.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("market-profile.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run pytest, expect 2/2 pass**

Run: `python -m pytest tests/phase-niche/test-validate-market-profile.py -v`

- [ ] **Step 7: Commit**

```
git add skills/niche-analysis/scripts/validate-market-profile.py tests/phase-niche/test-validate-market-profile.py tests/phase-niche/fixtures/market-profile-*.md
git commit -m "$(cat <<'EOF'
feat(market-profile): validator + fixtures

Plan task 4/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Шаблоны positioning.md — фикстуры для 3 режимов

**Files:**
- Create: `tests/phase-niche/fixtures/positioning-rational-valid.md`
- Create: `tests/phase-niche/fixtures/positioning-emotional-valid.md`
- Create: `tests/phase-niche/fixtures/positioning-trust-valid.md`
- Create: `tests/phase-niche/fixtures/positioning-no-mode-header.md`
- Create: `tests/phase-niche/fixtures/positioning-mode-template-mismatch.md`

- [ ] **Step 1: Create rational fixture**

`tests/phase-niche/fixtures/positioning-rational-valid.md`:

```markdown
# Позиционирование: Test Drilling Co

**Mode:** rational

## Job statement
Когда мне нужна вода на участке, я хочу заказать бурение, чтобы получить гарантированный объём воды с понятными сроками и ценой.

## Desired outcomes
- Вода в течение 3 рабочих дней
- Гарантия глубины
- Фиксированная цена без сюрпризов

## Metrics that matter
| Метрика | Наш показатель | Бенчмарк ниши |
|---|---|---|
| Срок | 3 дня | 5–7 дней |
| Гарантия | 5 лет | 1–2 года |

## Functional benefit ladder
1. **Feature:** Гидрогеолог-выезд
   **Benefit:** Точка бурения подобрана научно
   **Outcome:** Минимизирован риск пустой скважины

## Чего избегать
- Эмоциональные обещания без подтверждения
```

- [ ] **Step 2: Create emotional fixture**

`tests/phase-niche/fixtures/positioning-emotional-valid.md`:

```markdown
# Позиционирование: Test Premium Brand

**Mode:** emotional_aspiration

## 1. Character
Семейный мужчина 40+, предприниматель в Дубае. Видит себя успешным.

## 2. Problem
**External:** нужен большой семейный SUV
**Internal:** устал от компромиссов
**Philosophical:** семья заслуживает лучшего

## 3. Guide
Эмпатия + авторитет.

## 4. Plan
1. Запросить тест-драйв
2. Приехать в шоурум
3. Выбрать комплектацию

## 5. Call to Action
- Direct: запросить тест-драйв
- Transitional: посмотреть модели

## 6. Success vision
Глава семьи, который не поступился ничем.

## 7. Failure vision
Очередной компромисс.

## Tone of voice
- Уверенный, тёплый, безупречный

## Чего избегать
- Сухой functional copy
```

- [ ] **Step 3: Create trust fixture**

`tests/phase-niche/fixtures/positioning-trust-valid.md`:

```markdown
# Позиционирование: Test Clinic

**Mode:** trust_authority

## Authority signals
**Кто мы и почему нам можно доверять:**
- Опыт: 15 лет
- Регалии: лицензия №12345

## Process transparency
1. Консультация
2. Диагностика
3. Лечение

## Social proof tiers
**Tier 1:** отзывы коллег
**Tier 2:** 2400 успешных кейсов
**Tier 3:** отзывы пациентов

## Risk reversal
Гарантия результата.

## Чего избегать
- Stock business meeting photos
```

- [ ] **Step 4: Create no-mode-header fixture**

`tests/phase-niche/fixtures/positioning-no-mode-header.md`:

```markdown
# Позиционирование: Broken

## Some section
text without Mode header
```

- [ ] **Step 5: Create mode-template mismatch fixture**

`tests/phase-niche/fixtures/positioning-mode-template-mismatch.md`:

```markdown
# Позиционирование: Mismatch

**Mode:** rational

## Character
This is StoryBrand format but Mode says rational

## Problem
External: ...
```

(Mode = rational, but only emotional-template sections present.)

- [ ] **Step 6: Commit fixtures**

```
git add tests/phase-niche/fixtures/positioning-*.md
git commit -m "$(cat <<'EOF'
test(positioning): fixtures for 3 modes + 2 invalid cases

Plan task 5/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Валидатор `validate-positioning.py` (mode-aware)

**Files:**
- Create: `skills/niche-analysis/scripts/validate-positioning.py`
- Create: `tests/phase-niche/test-validate-positioning.py`

- [ ] **Step 1: Write failing pytest**

`tests/phase-niche/test-validate-positioning.py`:

```python
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-positioning.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_rational_passes():
    r = run("positioning-rational-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_emotional_passes():
    r = run("positioning-emotional-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_trust_passes():
    r = run("positioning-trust-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_no_mode_header_fails():
    r = run("positioning-no-mode-header.md")
    assert r.returncode != 0
    assert "mode" in (r.stdout + r.stderr).lower()


def test_mode_template_mismatch_fails():
    r = run("positioning-mode-template-mismatch.md")
    assert r.returncode != 0
    out = (r.stdout + r.stderr).lower()
    assert "section" in out or "missing" in out
```

- [ ] **Step 2: Run pytest, expect 5 failures (script doesn't exist)**

- [ ] **Step 3: Implement mode-aware validator**

`skills/niche-analysis/scripts/validate-positioning.py`:

```python
#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/positioning.md — mode-aware.

1. Reads `**Mode:** <mode>` header.
2. Loads template sections for that mode from config/positioning-modes.yaml.
3. Verifies all template sections are present (regex headers).

Exits 0 on valid, 1 on errors.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed.", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[3]
MODES_YAML = REPO_ROOT / "config" / "positioning-modes.yaml"

VALID_MODE_RE = re.compile(
    r"^(rational|emotional_aspiration|trust_authority|hybrid:[a-z_]+\+[a-z_]+|legacy_v1)$",
    re.IGNORECASE,
)


def load_modes():
    return yaml.safe_load(MODES_YAML.read_text(encoding="utf-8"))


def section_to_pattern(title: str) -> str:
    """Convert template_section title to a header regex.

    'Job statement' -> r'##\\s+(?:\\d+\\.\\s+)?Job\\s+statement'
    Allows numbered (## 1. Title) or unnumbered (## Title) headings.
    """
    escaped = re.escape(title).replace(r"\ ", r"\s+")
    return rf"^##\s+(?:\d+(?:\.\d+)?\.\s+)?{escaped}\s*$"


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    # Mode header
    mode_match = re.search(r"^\*\*Mode:\*\*\s*([a-z_+:]+)", text, re.MULTILINE | re.IGNORECASE)
    if not mode_match:
        return ["Missing **Mode:** header"]
    mode_raw = mode_match.group(1).strip().lower()
    if not VALID_MODE_RE.match(mode_raw):
        return [f"Invalid Mode value: '{mode_raw}'"]

    # Determine which template to validate
    if mode_raw == "legacy_v1":
        return []  # legacy migration stub — skip template check
    if mode_raw.startswith("hybrid:"):
        primary = mode_raw.split(":", 1)[1].split("+")[0]
    else:
        primary = mode_raw

    modes = load_modes()
    template = modes.get("modes", {}).get(primary)
    if not template:
        return [f"Mode '{primary}' not found in positioning-modes.yaml"]

    sections = template.get("template_sections", [])
    for sec_title in sections:
        pattern = section_to_pattern(sec_title)
        if not re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
            errors.append(f"Section '{sec_title}' missing for mode '{primary}'")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-positioning.py <positioning.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("positioning.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run pytest, expect 5/5 pass**

Run: `python -m pytest tests/phase-niche/test-validate-positioning.py -v`

- [ ] **Step 5: Commit**

```
git add skills/niche-analysis/scripts/validate-positioning.py tests/phase-niche/test-validate-positioning.py
git commit -m "$(cat <<'EOF'
feat(positioning): mode-aware validator

Plan task 6/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Фикстуры landing-structure.md

**Files:**
- Create: `tests/phase-niche/fixtures/landing-structure-valid.md`
- Create: `tests/phase-niche/fixtures/landing-structure-missing-hero.md`

- [ ] **Step 1: Valid fixture**

`tests/phase-niche/fixtures/landing-structure-valid.md`:

```markdown
# Структура лендинга: Test

> Тип бренда: 2
> Режим: emotional_aspiration
> Дата: 2026-05-06

## Блоки лендинга (в порядке отображения)

| # | Блок | Обязательный? | Цель | Содержание (откуда) |
|---|---|---|---|---|
| 1 | Hero | yes | hook | positioning §3 |
| 2 | Brand short story | yes | trust | brand-kit §1 |
| 3 | Featured Models | yes | catalog | models data |
| 4 | Trust signals | yes | warranty | brief |
| 5 | CTA | yes | conversion | positioning §5 |
| 6 | FAQ | optional | objections | content |
| 7 | Footer | yes | legal | brief |

## Обоснование выбора структуры
Тип 2 + emotional_aspiration: brand story нужна (региональный бренд),
catalog — основной контент, lifestyle опционален.

## Что НЕ включаем (и почему)
- About-Founder: бренд не personality-driven

## Контракт с wp-builder
Список template-parts:
- block-hero.php
- block-brand-story.php
- block-models.php
- block-trust.php
- block-cta.php
- block-faq.php
- block-footer.php
```

- [ ] **Step 2: Invalid fixture (no Hero)**

`tests/phase-niche/fixtures/landing-structure-missing-hero.md`:

```markdown
# Структура лендинга: Broken

> Тип бренда: 2
> Режим: emotional_aspiration

## Блоки лендинга (в порядке отображения)

| # | Блок | Обязательный? | Цель | Содержание |
|---|---|---|---|---|
| 1 | Brand story | yes | trust | kit |
| 2 | CTA | yes | conv | pos |
| 3 | Footer | yes | legal | brief |

## Обоснование выбора структуры
no Hero on purpose

## Что НЕ включаем
nothing

## Контракт с wp-builder
- block-brand-story.php
```

(Hero missing — must fail.)

- [ ] **Step 3: Commit fixtures**

```
git add tests/phase-niche/fixtures/landing-structure-*.md
git commit -m "$(cat <<'EOF'
test(landing-structure): valid + missing-hero fixtures

Plan task 7/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Валидатор `validate-landing-structure.py`

**Files:**
- Create: `skills/niche-analysis/scripts/validate-landing-structure.py`
- Create: `tests/phase-niche/test-validate-landing-structure.py`

- [ ] **Step 1: Write failing pytest**

`tests/phase-niche/test-validate-landing-structure.py`:

```python
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "niche-analysis" / "scripts" / "validate-landing-structure.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run(name):
    return subprocess.run(
        ["python", str(SCRIPT), str(FIXTURES / name)],
        capture_output=True, text=True
    )


def test_valid_passes():
    r = run("landing-structure-valid.md")
    assert r.returncode == 0, r.stderr or r.stdout


def test_missing_hero_fails():
    r = run("landing-structure-missing-hero.md")
    assert r.returncode != 0
    assert "hero" in (r.stdout + r.stderr).lower()
```

- [ ] **Step 2: Run pytest, expect 2 failures**

- [ ] **Step 3: Implement validator**

`skills/niche-analysis/scripts/validate-landing-structure.py`:

```python
#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/landing-structure.md.

Required:
- Frontmatter-style headers: Тип бренда, Режим
- Section "Блоки лендинга" with markdown table containing Hero, CTA, Footer
- Section "Обоснование выбора структуры"
- Section "Контракт с wp-builder"

Exits 0 on valid, 1 on errors.
"""
import re
import sys
from pathlib import Path


REQUIRED_BLOCKS = {"hero", "cta", "footer"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    # Required sections
    for header in (
        r"##\s+Блоки\s+лендинга",
        r"##\s+Обоснование\s+выбора\s+структуры",
        r"##\s+Контракт\s+с\s+wp-builder",
    ):
        if not re.search(header, text, re.IGNORECASE):
            errors.append(f"Section missing: {header}")

    # Required headers in frontmatter
    if not re.search(r">\s*Тип\s+бренда:\s*[123]", text, re.IGNORECASE):
        errors.append("Header missing: > Тип бренда: 1|2|3")
    if not re.search(r">\s*Режим:\s*[a-z_+:]+", text, re.IGNORECASE):
        errors.append("Header missing: > Режим: <mode>")

    # Required blocks in the block table — search for them as table cells
    text_lower = text.lower()
    for block in REQUIRED_BLOCKS:
        # Match "| Hero |" or "| hero |" (with extra whitespace)
        if not re.search(rf"\|\s*{re.escape(block)}\b", text_lower):
            errors.append(f"Required block missing in table: {block}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate-landing-structure.py <landing-structure.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("landing-structure.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run pytest, expect 2/2 pass**

Run: `python -m pytest tests/phase-niche/test-validate-landing-structure.py -v`

- [ ] **Step 5: Commit**

```
git add skills/niche-analysis/scripts/validate-landing-structure.py tests/phase-niche/test-validate-landing-structure.py
git commit -m "$(cat <<'EOF'
feat(landing-structure): validator

Plan task 8/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Полный pytest suite через явные пути

**Files:**
- Modify: `package.json`

Pytest пропускает файлы с дефисом в имени. Нужно явно перечислить тесты в npm-script.

- [ ] **Step 1: Update test:phase-niche script**

В `package.json` заменить существующий `"test:phase-niche"` на:

```json
"test:phase-niche": "bats tests/phase-niche/ && python -m pytest tests/phase-niche/test-validate-competitors.py tests/phase-niche/test-validate-visual-requirements.py tests/phase-niche/test-validate-market-profile.py tests/phase-niche/test-validate-positioning.py tests/phase-niche/test-validate-landing-structure.py -v"
```

- [ ] **Step 2: Run it, expect green**

Run: `npm run test:phase-niche`
Expected: all bats and all pytests pass.

- [ ] **Step 3: Commit**

```
git add package.json
git commit -m "$(cat <<'EOF'
chore(stage-01a-v2): npm test:phase-niche includes new validators

Plan task 9/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# Phase C: Agent integration

## Task 10: niche-analyst — шаг 4 (Рыночный профиль)

**Files:**
- Modify: `agents/niche-analyst.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing bats tests**

```bash
@test "niche-analyst documents step 4 market profile" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "market-profile.md" "$AGENT"
}

@test "niche-analyst lists market-profile.md in outputs" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -E "^[0-9]+\.\s+\`market-profile.md\`" "$AGENT"
}
```

- [ ] **Step 2: Run tests, verify 2 failures**

- [ ] **Step 3: Edit `agents/niche-analyst.md`**

In Outputs section, add 5th item (after `visual-requirements.md`):

```markdown
5. `market-profile.md` — рыночный профиль: accessibility tier (relative price), consideration cycle, decision unit, regulated, emotional load, cultural context. Структура и валидатор: `skills/niche-analysis/scripts/validate-market-profile.py`.
```

In Algorithm section, after step 3 (classification of brand type), insert step 4:

```markdown
4. **Рыночный профиль.** Записать `market-profile.md`:
   1. **Accessibility tier:** WebSearch медианного дохода региона. Сопоставить цену клиента (из брифа или медианы competitors.yaml) с медианным доходом. Назначить tier из 6 уровней: utility_essential | mass_consumer | mid_premium | premium | luxury_status | ultra_luxury. Sanity-check: если категория глобально luxury (Hermès, Bentley), переопределить через категорийный признак.
   2. **Consideration cycle:** определить от категории (impulse | short | medium | long | very_long).
   3. **Decision unit:** individual | family | corporate.
   4. **Regulated:** yes/no — медицина, право, финансы, образование.
   5. **Emotional load:** low/medium/high.
   6. **Cultural context:** короткое описание рынка (статус-коды, отношение к иностранным брендам, локальные привычки).
   7. **Predicted mode:** на основе матрицы из `config/positioning-modes.yaml`.
   8. Источники и допущения (URL, [ДОПУЩЕНИЕ] при нехватке данных).
```

(Соответственно сдвинуть нумерацию старых шагов 4–9: были «4. Сбор конкурентов» теперь «5. Сбор конкурентов» и т.д.)

- [ ] **Step 4: Run tests, verify all pass**

- [ ] **Step 5: Commit**

```
git add agents/niche-analyst.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(niche-analyst): step 4 — market profile

Plan task 10/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: niche-analyst — шаг 7 (Классификация режима) и шаг 8 (Позиционирование по шаблону)

**Files:**
- Modify: `agents/niche-analyst.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing tests**

```bash
@test "niche-analyst documents step 7 mode classification" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "positioning-modes.yaml\|Predicted mode" "$AGENT"
}

@test "niche-analyst documents 3 positioning templates" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "rational" "$AGENT"
  grep -q "emotional_aspiration" "$AGENT"
  grep -q "trust_authority" "$AGENT"
}
```

- [ ] **Step 2: Run tests, expect 2 failures**

- [ ] **Step 3: Edit `agents/niche-analyst.md`**

After existing «6. Скрейп конкурентов» step (renumbered from 5 in Task 10), insert:

```markdown
7. **Классификация режима позиционирования.**
   1. Прочитать `market-profile.md` → predicted mode.
   2. Прочитать индикаторы из брифа/контекста (`brief_indicators` в `config/positioning-modes.yaml`).
   3. Если индикаторы конфликтуют с predicted mode → выбрать доминирующий маркер, пометить `[ДОПУЩЕНИЕ]`.
   4. Если в брифе явный override от клиента/маркетолога — он перевешивает.
   5. Финальный режим: `rational` | `emotional_aspiration` | `trust_authority` | `hybrid:X+Y`.

8. **Позиционирование по шаблону.** Записать `positioning.md`:
   1. Заголовок `**Mode:** <mode>`.
   2. Заполнить шаблон выбранного режима (template_sections из `config/positioning-modes.yaml`):
      - **rational:** Job statement / Desired outcomes / Metrics that matter / Functional benefit ladder / Чего избегать
      - **emotional_aspiration:** StoryBrand 7-part: Character / Problem (3 уровня) / Guide / Plan / Call to Action / Success vision / Failure vision / Tone of voice / Чего избегать
      - **trust_authority:** Authority signals / Process transparency / Social proof tiers / Risk reversal / Чего избегать
   3. Для `hybrid:X+Y` — заполнить шаблон primary (X), добавить секцию «Secondary mode signals (Y)» с 2–3 дополнительными элементами.
   4. Запустить валидатор: `python skills/niche-analysis/scripts/validate-positioning.py <path>`.
```

(Старые шаги «7. Синтез позиционирования» и «8. Самопроверка competitors» становятся частью этих новых шагов или сдвигаются дальше.)

- [ ] **Step 4: Run tests, all pass**

- [ ] **Step 5: Commit**

```
git add agents/niche-analyst.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(niche-analyst): steps 7-8 — mode classification + positioning template

Plan task 11/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: niche-analyst — шаг 9 (Карта структуры лендинга)

**Files:**
- Modify: `agents/niche-analyst.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing test**

```bash
@test "niche-analyst documents step 9 landing structure" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/niche-analyst.md"
  grep -q "landing-structure.md" "$AGENT"
}
```

- [ ] **Step 2: Run tests, expect 1 failure**

- [ ] **Step 3: Edit `agents/niche-analyst.md`**

After step 8 (positioning), insert:

```markdown
9. **Карта структуры лендинга.** Записать `landing-structure.md`:
   1. Зафиксировать `Тип бренда: <1|2|3>` и `Режим: <mode>` в frontmatter.
   2. На основе типа бренда + режима выбрать рекомендованную карту блоков (см. spec §6 шаблонные карты для 9 комбинаций).
   3. Адаптировать карту под конкретный проект:
      - Тип 1 (глобальный): убрать «Brand story» если не нужен (бренд узнаваем).
      - Тип 2 (региональный): добавить «Brand short story» (1 экран).
      - Тип 3 (локальный): обязательно «About», «Reviews», часто «Pricing».
   4. Cultural adjustments: добавить блоки специфичные для рынка (халяль для арабских рынков, sustainability для скандинавских и т.д.).
   5. Заполнить таблицу блоков с обязательным указанием Hero, CTA, Footer.
   6. Заполнить раздел «Контракт с wp-builder» — список template-parts.
   7. Запустить валидатор: `python skills/niche-analysis/scripts/validate-landing-structure.py <path>`.
```

Также добавить пункт в Outputs:

```markdown
6. `landing-structure.md` — карта блоков лендинга по типу бренда + режиму. Структура и валидатор: `skills/niche-analysis/scripts/validate-landing-structure.py`.
```

- [ ] **Step 4: Run tests, all pass**

- [ ] **Step 5: Commit**

```
git add agents/niche-analyst.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(niche-analyst): step 9 — landing structure artifact

Plan task 12/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# Phase D: Downstream contracts

## Task 13: brand-architect читает market-profile + landing-structure

**Files:**
- Modify: `agents/brand-architect.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing tests**

```bash
@test "brand-architect reads market-profile.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/brand-architect.md"
  grep -q "market-profile.md" "$AGENT"
}

@test "brand-architect reads landing-structure.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/brand-architect.md"
  grep -q "landing-structure.md" "$AGENT"
}
```

- [ ] **Step 2: Run tests, expect 2 failures**

- [ ] **Step 3: Edit `agents/brand-architect.md`**

Find existing «Inputs from earlier stages» section (added previously for positioning.md). Append:

```markdown
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — обязательный input. Cultural context (Section 6) и accessibility tier (Section 1) определяют, какой brand-kit уместен (для luxury_status — больше white space, минимум pop, эксклюзивность; для mass_consumer — больше contrast и call-out'ов).
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — обязательный input. Brand-kit должен покрывать все блоки из таблицы (если в карте есть «About-Founder» — нужен portrait style guide).
```

- [ ] **Step 4: Run tests, all pass**

- [ ] **Step 5: Commit**

```
git add agents/brand-architect.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(brand-architect): read market-profile + landing-structure

Plan task 13/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: content-writer распознаёт mode + читает landing-structure

**Files:**
- Modify: `agents/content-writer.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing tests**

```bash
@test "content-writer reads landing-structure.md" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/content-writer.md"
  grep -q "landing-structure.md" "$AGENT"
}

@test "content-writer recognizes positioning Mode" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/content-writer.md"
  grep -q "Mode\|mode\|emotional_aspiration\|trust_authority\|rational" "$AGENT"
}
```

- [ ] **Step 2: Run tests, expect 2 failures (mode test may pass already through inherited mention)**

- [ ] **Step 3: Edit `agents/content-writer.md`**

In existing «Inputs from earlier stages» section, append:

```markdown
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — обязательный input. Контент пишется **по структуре блоков из таблицы**, не угадывается. Каждому блоку из «Контракт с wp-builder» соответствует один заголовок в `final-copy.md`.
- `01a_АНАЛИЗ_НИШИ/positioning.md` — обязательный input, теперь mode-aware. Прочитать `**Mode:** <mode>` в начале файла:
  - **rational:** факты, цифры, ROI, без эмоциональных украшений
  - **emotional_aspiration:** StoryBrand-нарратив, картина «успех vs failure», sensory language
  - **trust_authority:** authority statements, конкретные цифры опыта, transparent process
  - **hybrid:X+Y:** primary mode задаёт основной тон, secondary даёт 1–2 поддерживающих элемента.
```

- [ ] **Step 4: Run tests, all pass**

- [ ] **Step 5: Commit**

```
git add agents/content-writer.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(content-writer): mode-aware copy + landing-structure as block source

Plan task 14/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 15: wp-builder генерирует темы по landing-structure

**Files:**
- Modify: `agents/wp-builder.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing test**

```bash
@test "wp-builder uses landing-structure for template generation" {
  AGENT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../agents" && pwd)/wp-builder.md"
  grep -q "landing-structure.md" "$AGENT"
}
```

- [ ] **Step 2: Run tests, expect 1 failure**

- [ ] **Step 3: Edit `agents/wp-builder.md`**

Existing «Visual sanity-checks» section was added previously. Add new section after it:

```markdown

## Landing structure as build contract

Перед генерацией темы:

1. **Прочитать `01a_АНАЛИЗ_НИШИ/landing-structure.md`** — раздел «Контракт с wp-builder».
2. **Сгенерировать строго те template-parts, которые перечислены.** Не добавлять блоки, которых нет в карте.
3. **Hero focal point** определяется секцией Hero из карты + visual-requirements.md.
4. **Если карта говорит accessibility_tier=luxury_status** (читать из market-profile.md) — НЕ показывать price prominently в Hero. Цена раскрывается только при запросе («request a quote»).
5. **Порядок блоков** в `front-page.php` — точно как в таблице карты. Не переставлять «по дизайну».
```

- [ ] **Step 4: Run tests, all pass**

- [ ] **Step 5: Commit**

```
git add agents/wp-builder.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(wp-builder): generate themes per landing-structure contract

Plan task 15/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# Phase E: Gate-check & docs

## Task 16: stage-gates.yaml — 3 новых hard_check

**Files:**
- Modify: `config/stage-gates.yaml`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing tests**

```bash
@test "stage-gates 01a includes market_profile_md hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "market_profile_md" "$GATES"
}

@test "stage-gates 01a includes landing_structure_md hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "landing_structure_md" "$GATES"
}

@test "stage-gates 01a includes positioning_schema hard check" {
  GATES="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../config" && pwd)/stage-gates.yaml"
  grep -q "positioning_schema" "$GATES"
}
```

- [ ] **Step 2: Run tests, expect 3 failures**

- [ ] **Step 3: Edit `config/stage-gates.yaml`**

In `01a_niche_analysis` block, in `hard_checks` array (after `visual_requirements_schema`), append:

```yaml
      - id: market_profile_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/market-profile.md"
        required: true
        fix_hint: "niche-analyst agent creates this (step 4)"
      - id: market_profile_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-market-profile.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/market-profile.md"]
        required: true
        fix_hint: "Fix market-profile.md sections — see script output"
      - id: positioning_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-positioning.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/positioning.md"]
        required: true
        fix_hint: "Fix positioning.md — Mode header + template sections"
      - id: landing_structure_md
        type: file_exists
        path: "{project}/01a_АНАЛИЗ_НИШИ/landing-structure.md"
        required: true
        fix_hint: "niche-analyst agent creates this (step 9)"
      - id: landing_structure_schema
        type: script
        script: "skills/niche-analysis/scripts/validate-landing-structure.py"
        args: ["{project}/01a_АНАЛИЗ_НИШИ/landing-structure.md"]
        required: true
        fix_hint: "Fix landing-structure.md — Hero/CTA/Footer required"
```

- [ ] **Step 4: Validate yaml**

`python -c "import yaml; yaml.safe_load(open('config/stage-gates.yaml', encoding='utf-8'))"` → exit 0.

- [ ] **Step 5: Run tests, all pass**

- [ ] **Step 6: Commit**

```
git add config/stage-gates.yaml tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
feat(stage-gates): require market-profile + positioning_schema + landing-structure

Plan task 16/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 17: template README обновляется на 6 артефактов

**Files:**
- Modify: `template/01a_АНАЛИЗ_НИШИ/README.md`
- Modify: `tests/phase-niche/test-niche-stage.bats`

- [ ] **Step 1: Append failing tests**

```bash
@test "template 01a README mentions market-profile.md" {
  README="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template/01a_АНАЛИЗ_НИШИ" && pwd)/README.md"
  grep -q "market-profile.md" "$README"
}

@test "template 01a README mentions landing-structure.md" {
  README="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../template/01a_АНАЛИЗ_НИШИ" && pwd)/README.md"
  grep -q "landing-structure.md" "$README"
}
```

- [ ] **Step 2: Run tests, expect 2 failures**

- [ ] **Step 3: Edit `template/01a_АНАЛИЗ_НИШИ/README.md`**

In «Артефакты» section, append:

```markdown
- `market-profile.md` — рыночный профиль: accessibility tier (по медианному доходу региона), consideration cycle, decision unit, regulated, emotional load, cultural context. Источник: WebSearch медианных доходов + competitors.yaml.
- `landing-structure.md` — карта блоков лендинга: что показываем в каком порядке, в зависимости от типа бренда + режима позиционирования. Источник: spec §6 шаблонные карты.
```

В «Что читает после», append:

```markdown
- `brand-architect` (этап 04) — `market-profile.md` + `landing-structure.md`
- `content-writer` (этап 07) — `landing-structure.md` (как контракт по блокам)
- `wp-builder` (этап 08) — `landing-structure.md` (как контракт по template-parts)
```

- [ ] **Step 4: Run tests, all pass**

- [ ] **Step 5: Commit**

```
git add template/01a_АНАЛИЗ_НИШИ/README.md tests/phase-niche/test-niche-stage.bats
git commit -m "$(cat <<'EOF'
docs(stage-01a-v2): template README — 6 artifacts

Plan task 17/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 18: Главный README — короткое упоминание v2

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current Status section**

Run: `grep -n "Stages\|01a\|v2" README.md | head -10`

- [ ] **Step 2: Update Stages line**

Найти строку:
```
**Stages (этапы 00–12 + 01a)**
```

Заменить на:
```
**Stages (этапы 00–12 + 01a v2)** — пользовательский workflow внутри одного лендинга. Этап 01a включает 6 артефактов: бриф/контекст-анализ, конкурентов, рыночный профиль, позиционирование (mode-aware), карту структуры, визуальные требования.
```

- [ ] **Step 3: Commit**

```
git add README.md
git commit -m "$(cat <<'EOF'
docs(readme): mention 01a v2 with 6 artifacts

Plan task 18/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# Phase F: Migration & smoke

## Task 19: Миграционный скрипт `migrate-niche-to-v2.sh`

**Files:**
- Create: `scripts/migrate-niche-to-v2.sh`
- Create: `tests/phase-niche/test-migrate-niche-to-v2.bats`

- [ ] **Step 1: Write failing bats tests**

`tests/phase-niche/test-migrate-niche-to-v2.bats`:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  TMP="$BATS_TEST_TMPDIR"
  PROJECT="$TMP/legacy-project"
  mkdir -p "$PROJECT/01a_АНАЛИЗ_НИШИ"

  # Create v1 artifacts (4 of them)
  printf "# stub niche analysis\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/niche-analysis.md"
  printf "competitors:\n  - {name: X, role: direct}\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/competitors.yaml"
  printf "# stub positioning\n## Core promise\nold v1 format\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md"
  printf "# stub visual requirements\n" > "$PROJECT/01a_АНАЛИЗ_НИШИ/visual-requirements.md"
}

@test "migrate creates market-profile.md stub" {
  bash "$REPO/scripts/migrate-niche-to-v2.sh" "$PROJECT"
  [ -f "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md" ]
  grep -q "ДОПУЩЕНИЕ" "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md"
}

@test "migrate creates landing-structure.md stub" {
  bash "$REPO/scripts/migrate-niche-to-v2.sh" "$PROJECT"
  [ -f "$PROJECT/01a_АНАЛИЗ_НИШИ/landing-structure.md" ]
}

@test "migrate adds Mode: legacy_v1 to positioning.md" {
  bash "$REPO/scripts/migrate-niche-to-v2.sh" "$PROJECT"
  grep -q "Mode:.*legacy_v1" "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md"
}

@test "migrate is idempotent (rerun does not break files)" {
  bash "$REPO/scripts/migrate-niche-to-v2.sh" "$PROJECT" >/dev/null
  bash "$REPO/scripts/migrate-niche-to-v2.sh" "$PROJECT" >/dev/null
  [ -f "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md" ]
  # Mode should appear exactly once
  count=$(grep -c "Mode:.*legacy_v1" "$PROJECT/01a_АНАЛИЗ_НИШИ/positioning.md")
  [ "$count" -eq 1 ]
}
```

- [ ] **Step 2: Run tests, expect 4 failures**

- [ ] **Step 3: Implement migration script**

`scripts/migrate-niche-to-v2.sh`:

```bash
#!/usr/bin/env bash
# scripts/migrate-niche-to-v2.sh
# Migrate legacy v1 niche-analysis (4 artifacts) to v2 (6 artifacts) by adding stubs.
# Idempotent: safe to re-run.
set -euo pipefail

PROJECT="${1:?usage: migrate-niche-to-v2.sh <project-dir>}"
DIR="$PROJECT/01a_АНАЛИЗ_НИШИ"

[ -d "$DIR" ] || { echo "ERROR: $DIR not found" >&2; exit 1; }

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# 1. market-profile.md stub
MP="$DIR/market-profile.md"
if [ ! -f "$MP" ]; then
    cat > "$MP" <<'EOF'
# Рыночный профиль: [LEGACY MIGRATION STUB]

> Дата: STUB
> Регион: [ДОПУЩЕНИЕ] требуется ручное заполнение

## 1. Accessibility tier
**Tier:** mid_premium

**Обоснование:**
- [ДОПУЩЕНИЕ] миграция от v1, требуется ручное заполнение
- Цена клиента/категории: TBD
- Медианный доход региона: TBD

## 2. Consideration cycle
**Тип:** medium
[ДОПУЩЕНИЕ]

## 3. Decision unit
**Тип:** individual
[ДОПУЩЕНИЕ]

## 4. Regulated category
**Регулируется:** no
[ДОПУЩЕНИЕ]

## 5. Emotional load
**Уровень:** medium
[ДОПУЩЕНИЕ]

## 6. Cultural context
**Регион:** TBD
[ДОПУЩЕНИЕ]

## 7. Сводная рекомендация режима
**Predicted mode:** legacy_v1

## 8. Источники и допущения
- [ДОПУЩЕНИЕ] весь файл — миграционный stub. Требуется ручное заполнение для нового пайплайна v2.
EOF
    echo "Created $MP (legacy stub)"
fi

# 2. landing-structure.md stub
LS="$DIR/landing-structure.md"
if [ ! -f "$LS" ]; then
    cat > "$LS" <<'EOF'
# Структура лендинга: [LEGACY MIGRATION STUB]

> Тип бренда: 2
> Режим: legacy_v1
> Дата: STUB

## Блоки лендинга (в порядке отображения)

| # | Блок | Обязательный? | Цель | Содержание (откуда) |
|---|---|---|---|---|
| 1 | Hero | yes | hook | legacy |
| 2 | CTA | yes | conversion | legacy |
| 3 | Footer | yes | legal | legacy |

## Обоснование выбора структуры
[ДОПУЩЕНИЕ] миграционный stub. Реальная структура существующего лендинга может отличаться.

## Что НЕ включаем (и почему)
- [ДОПУЩЕНИЕ]

## Контракт с wp-builder
- block-hero.php
- block-cta.php
- block-footer.php
EOF
    echo "Created $LS (legacy stub)"
fi

# 3. Add Mode: legacy_v1 to positioning.md if missing
POS="$DIR/positioning.md"
if [ -f "$POS" ]; then
    if ! grep -q "Mode:.*legacy_v1" "$POS"; then
        # Insert after first heading
        tmpfile="$(mktemp)"
        awk 'NR==1 {print; print ""; print "**Mode:** legacy_v1"; next} {print}' "$POS" > "$tmpfile"
        mv "$tmpfile" "$POS"
        echo "Added Mode: legacy_v1 to $POS"
    fi
fi

echo "Migration done."
```

Make executable: `chmod +x scripts/migrate-niche-to-v2.sh`

- [ ] **Step 4: Run tests, expect 4/4 pass**

`bats tests/phase-niche/test-migrate-niche-to-v2.bats`

- [ ] **Step 5: Commit**

```
git add scripts/migrate-niche-to-v2.sh tests/phase-niche/test-migrate-niche-to-v2.bats
git commit -m "$(cat <<'EOF'
feat(stage-01a-v2): migrate-niche-to-v2 script for legacy projects

Plan task 19/22.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 20: Smoke test on lixiang-dubai (manual)

**Files:**
- Create (manual, в lixiang проекте, не в репо): `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/market-profile.md`
- Create: `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/landing-structure.md`
- Modify: `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/positioning.md` (rewrite в emotional_aspiration шаблоне)

Smoke-проверка живой методики на реальном проекте.

- [ ] **Step 1: Run migration on lixiang first (creates stubs)**

```
bash scripts/migrate-niche-to-v2.sh /d/AI_TEAMS/Lendings/lixiang-dubai
```

- [ ] **Step 2: Manually rewrite market-profile.md for lixiang**

Заполнить рыночный профиль: ОАЭ, AED 250k, медианный доход AED ~25k → tier `premium`. Decision: family. Regulated: no. Emotional load: medium-high. Cultural: премиум-через-демонстрацию. Predicted mode: `emotional_aspiration`.

Записать в `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/market-profile.md` по структуре из spec §3.

- [ ] **Step 3: Manually rewrite positioning.md for lixiang в emotional_aspiration шаблоне**

Перезаписать `D:/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/positioning.md` по StoryBrand 7-part:
- Character: успешный экспат-предприниматель в Дубае, семьянин 40+
- Problem (3 уровня): семейный SUV / устал от компромиссов / семья заслуживает
- Guide: бренд + локальный дилер
- Plan: 3 шага
- CTA: запрос тест-драйва
- Success vision: глава семьи в L9, royal seating, кожа Nappa, никаких компромиссов
- Failure vision: ещё один год компромиссных машин

Заголовок `**Mode:** emotional_aspiration`.

- [ ] **Step 4: Manually rewrite landing-structure.md по карте Тип 2 + emotional_aspiration**

Из spec §6:
```
Hero (продукт + emotional hook)
→ Brand short story (1 экран)
→ Featured Models / Catalog
→ Experience/Lifestyle
→ Trust (warranty, service, GCC)
→ Test Drive / CTA
→ FAQ
→ Footer
```

- [ ] **Step 5: Run validators on all 6 artifacts**

```
python skills/niche-analysis/scripts/validate-market-profile.py /d/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/market-profile.md
python skills/niche-analysis/scripts/validate-positioning.py /d/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/positioning.md
python skills/niche-analysis/scripts/validate-landing-structure.py /d/AI_TEAMS/Lendings/lixiang-dubai/01a_АНАЛИЗ_НИШИ/landing-structure.md
```

Expected: all 3 → exit 0.

- [ ] **Step 6: Run gate-check on lixiang**

```
bash scripts/gate-check.sh --stage 01a_niche_analysis --project /d/AI_TEAMS/Lendings/lixiang-dubai --auto
```

Expected: all hard_checks green.

- [ ] **Step 7: No commit** (lixiang artifacts не в репо системы).

---

## Task 21: Полный test suite

- [ ] **Step 1: Run full bats**

```
npm test
```

Expected: all bats pass (300+ existing + new).

- [ ] **Step 2: Run full pytest with explicit paths**

```
python -m pytest tests/phase-niche/test-validate-competitors.py tests/phase-niche/test-validate-visual-requirements.py tests/phase-niche/test-validate-market-profile.py tests/phase-niche/test-validate-positioning.py tests/phase-niche/test-validate-landing-structure.py -v
```

Expected: 14+ pytest pass.

- [ ] **Step 3: Sanity-check на свежем проекте**

```
TMP="$(mktemp -d)"
PROJECT="$TMP/test-vr-flow"
mkdir -p "$PROJECT"
cp -r template/. "$PROJECT/"
yq -i '.stages."00_brief".status = "approved"' "$PROJECT/.landing-state.yaml"
bash scripts/gate-check.sh --stage 01a_niche_analysis --project "$PROJECT" --auto
```

Expected: gate-check fails with explicit list of missing artifacts (4 v1 artifacts + 2 new v2 artifacts).

---

## Task 22: Push + close

- [ ] **Step 1: Final git status check**

```
git status
git log --oneline 034fd51..HEAD
```

Expected: clean working tree, ~20 new commits.

- [ ] **Step 2: Push**

```
git push origin main
```

- [ ] **Step 3: Update todo / close**

Mark all tasks completed in TodoWrite.

---

## Self-Review

**1. Spec coverage:**

| Spec section | Tasks |
|---|---|
| §1 Цель и проблема | Tasks 10, 11, 12, 13, 14, 15 (всё реализует решение проблем A, B, C) |
| §2 Артефакты + 12 шагов | Tasks 4, 5, 6, 7, 8 (артефакты), 10, 11, 12 (шаги в агенте) |
| §3 market-profile.md | Tasks 4 (валидатор), 10 (агент шаг 4) |
| §4 Классификация режима | Tasks 1, 3 (матрица), 11 (агент шаг 7) |
| §5 3 шаблона positioning | Tasks 5 (фикстуры), 6 (валидатор), 11 (агент шаг 8) |
| §6 landing-structure | Tasks 7, 8 (валидатор), 12 (агент шаг 9) |
| §7 visual-requirements обновление | Не покрыт явной задачей — visual-requirements добавится в Task 12 (карта структуры) косвенно через ссылки. **Gap: добавить в Task 12 step рекомендацию обновить шаблон visual-requirements при необходимости.** Или оставить — раздел 8 в visual-requirements пока optional. Решение: оставить optional, в acceptance проверим вручную при smoke. |
| §8 Контракты с downstream | Tasks 13 (brand-architect), 14 (content-writer), 15 (wp-builder) |
| §9 gate-check 4 hard_check | Task 16 (5 hard_check добавлено — корректно для §9) |
| §10 справочник positioning-modes | Task 1 |
| §11 файлы | Покрыто всеми задачами |
| §12 backward compat | Task 19 (миграция), Task 20 (применение к lixiang) |
| §13 acceptance criteria | Tasks 20, 21 (smoke + полный suite) |

Все секции покрыты. §7 закрыт через optional acceptance.

**2. Placeholder scan:** Прошёл. Каждая задача имеет конкретный код, конкретные команды, конкретные ожидаемые результаты. Нет «implement later».

**3. Type consistency:**
- `market-profile.md`, `positioning.md`, `landing-structure.md` — везде одинаково
- `accessibility_tier` (snake_case) с 6 значениями — согласовано в Tasks 1, 4, 19
- `emotional_aspiration` / `rational` / `trust_authority` / `hybrid:X+Y` — согласовано везде
- `Mode:` header в positioning.md — Tasks 5, 6, 11, 14, 19
- 5 valid cycles, 3 decision_units, 3 emotional_loads — консистентно

OK.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-06-niche-analysis-v2-implementation-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review.

**2. Inline Execution** — execute tasks in this session via executing-plans, batch with checkpoints.

Учитывая что:
- 22 task'a (большой scope)
- Затронуты 7 markdown-файлов агентов и 3 yaml-конфига (легко ошибиться при ручном редактировании)
- Включена методическая работа (3 шаблона позиционирования) — критично качество

рекомендую **Subagent-Driven** для надёжности.

Который выбираешь?
