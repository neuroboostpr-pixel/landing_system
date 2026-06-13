# Reference-Driven Flow — Phase 2 (Zone A: источник истины и раскладка)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans.

**Goal:** Выполнить зону A спеки [2026-06-12-reference-driven-flow-spec.md](../specs/2026-06-12-reference-driven-flow-spec.md): прототип без потерь на всех форматах, правило трёх источников, референс=скриншот, composed.html=канон.

**Архитектура:** минимальные правки существующих скриптов prototype-import + новый стандарт `docs/standards/reference-driven-rules.md`, на который ссылаются агенты. TDD для кода, доки — текстом.

### Task A1.1: Кодировки utf-8 (тест-линт + фикс)
- Test: `tests/prototype-import/test_encoding_discipline.py` — AST-скан всех `skills/prototype-import/scripts/*.py` + `skills/block-composition/scripts/*.py`: каждый `read_text()`/`write_text()`/`open()` обязан иметь `encoding=`.
- Fix: `md-to-yaml.py:35`, `validate-prototype.py:30`, `validate-selections.py:17` (+ что найдёт тест).

### Task A1.2: Fidelity-гейт на все форматы + prototype.md канон
- `verify-prototype-fidelity.py`: `--prototype` принимает и `.md` (raw-текст как blob; галлюцинации по тому же blocklist; price-структурная проверка только для yaml).
- `gate-prototype-fidelity.py`:
  - канон-цель = `prototype.md` (если есть; иначе fallback prototype.yaml);
  - источники: `.docx` → extract-docx-text; `.pdf` → extract-pdf-text (текстовый слой); `.md`/`.txt` → сам файл; картинки (`.png/.jpg/.jpeg/.webp`) → OCR (pytesseract если установлен);
  - OCR недоступен / PDF сканированный → ЯВНОЕ предупреждение в stdout + fidelity-report.md c пометкой «полнота НЕ проверена», exit 0 (не молча).
- Tests: `tests/prototype-import/test_gate_all_formats.py` — md-источник прогоняется; pdf c текстовым слоем прогоняется; md-канон проверяется вместо yaml.

### Task A1.3: Гейты 07a: prototype.md обязателен, yaml опционален
- `config/stage-gates.yaml` 07a: `prototype_md_exists` (required) вместо `prototype_yaml_exists`; yaml оставить soft-замечанием в fix_hint.
- Обновить `skills/prototype-import/SKILL.md` + `agents/prototype-importer.md`: канон = prototype.md.

### Task A2+A4: Стандарт reference-driven-rules + composed канон
- Create `docs/standards/reference-driven-rules.md`: правило трёх источников, запреты (раскладка референса/выдуманные элементы), исключение «клиент явно указал», поблочная сверка перед сборкой, «composed.html = единственная правда о виде, сборка выводится из него».
- `agents/block-composer.md`, `agents/landing-orchestrator.md`, `commands/landing-compose.md` — ссылка на стандарт + чек-лист сверки.
- 07c_composed: soft_check `structure_matches_prototype`.

### Task A3: Референс = скриншот
- `agents/references-curator.md` + `commands/landing-references.md`: скриншот/описание от клиента = вход первого класса; ссылка недоступна → ОБЯЗАН запросить скриншот (молча пропустить = дефект); палитра — по пикселям скриншота (extract-palette, уже есть B23).

**Вне скоупа Phase 2:** OCR-зависимость в обязательные деп-чеки (отдельно), переписывание compose-механики (Zone C).
