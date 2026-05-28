# B27+B28 — Brand-Architect Routing + Decisions Log Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** (1) brand-architect различает концептуальные и локальные правки и маршрутизирует их правильно; (2) агенты фиксируют самостоятельные решения в `decisions.log.md` через оркестратор.

**Architecture:** Новый скрипт `scripts/log-decisions.py` читает временный файл `.stage-decisions/<stage>.md` и дописывает в `decisions.log.md`. Три агента (brand-architect, design-system-generator, block-composer) получают протокол формирования отклонений. Оркестратор вызывает `log-decisions.py` после каждого approve. Brand-architect получает явный routing правок.

**Tech Stack:** Python 3.10+, pytest, Markdown, bash.

**Зависимости:** B23+B24 должны быть реализованы — нужен `visual-concept.yaml`. Задачи 1→2→3 последовательны. Task 4 независима.

---

## File Structure

**Создать:**
- `scripts/log-decisions.py` — запись отклонений в decisions.log.md
- `tests/test_log_decisions.py` — тесты для log-decisions.py

**Изменить:**
- `agents/brand-architect.md` — routing правок + протокол отклонений
- `agents/design-system-generator.md` — протокол отклонений
- `agents/block-composer.md` — протокол отклонений
- `agents/landing-orchestrator.md` — вызов log-decisions.py после approve
- `template/` — добавить `.gitignore` для `.stage-decisions/`

---

## Task 1: Скрипт `log-decisions.py`

**Files:**
- Create: `scripts/log-decisions.py`
- Test: `tests/test_log_decisions.py`

- [ ] **Step 1: Написать failing тесты**

```python
# tests/test_log_decisions.py
import importlib.util
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "log-decisions.py"

def _load():
    spec = importlib.util.spec_from_file_location("log_decisions", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_creates_decisions_log_if_missing(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    log = project / "decisions.log.md"
    assert log.exists()

def test_appends_no_deviations_entry(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "04_brand" in content
    assert "нет отклонений" in content

def test_appends_deviations_from_file(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    decisions_dir = project / ".stage-decisions"
    decisions_dir.mkdir()
    dec_file = decisions_dir / "04_brand.md"
    dec_file.write_text(
        "- Типографика: Inter 700 (агент)\n- Иконки: Lucide (агент)\n",
        encoding="utf-8"
    )
    mod.append_decisions(str(project), "04_brand", str(dec_file))
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "Inter 700" in content
    assert "Lucide" in content
    assert "04_brand" in content

def test_appends_multiple_stages(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    mod.append_decisions(str(project), "05_design", None)
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "04_brand" in content
    assert "05_design" in content

def test_deletes_temp_file_after_append(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    decisions_dir = project / ".stage-decisions"
    decisions_dir.mkdir()
    dec_file = decisions_dir / "04_brand.md"
    dec_file.write_text("- Типографика: Inter 700\n", encoding="utf-8")
    mod.append_decisions(str(project), "04_brand", str(dec_file))
    assert not dec_file.exists()

def test_creates_header_on_first_run(tmp_path):
    mod = _load()
    project = tmp_path / "myproject"
    project.mkdir()
    mod.append_decisions(str(project), "04_brand", None)
    content = (project / "decisions.log.md").read_text(encoding="utf-8")
    assert "# Decisions Log" in content
```

- [ ] **Step 2: Запустить — убедиться что FAIL**

```bash
cd D:\AI_TEAMS\landing_system
python -m pytest tests/test_log_decisions.py -v
```

Ожидаем: `ModuleNotFoundError` или `FileNotFoundError`.

- [ ] **Step 3: Создать `scripts/log-decisions.py`**

```python
#!/usr/bin/env python3
"""Append stage decisions to <project>/decisions.log.md.

CLI:
  python scripts/log-decisions.py --project <path> --stage 04_brand
  python scripts/log-decisions.py --project <path> --stage 04_brand \
    --decisions-file <project>/.stage-decisions/04_brand.md
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path


LOG_FILENAME = "decisions.log.md"
HEADER = "# Decisions Log\n\nЖурнал самостоятельных решений агентов.\nФиксируется только то, что не было задано в visual-concept.yaml явно.\n\n"


def append_decisions(project: str, stage: str, decisions_file: str | None) -> None:
    project_path = Path(project)
    log_path = project_path / LOG_FILENAME

    # Create log with header if missing
    if not log_path.exists():
        log_path.write_text(HEADER, encoding="utf-8")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if decisions_file and Path(decisions_file).exists():
        content = Path(decisions_file).read_text(encoding="utf-8").strip()
        entry = f"\n## {stage} — {timestamp}\n\n{content}\n"
        Path(decisions_file).unlink()
    else:
        entry = f"\n## {stage} — {timestamp}\n\n_(нет отклонений)_\n"

    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--decisions-file", default=None, dest="decisions_file")
    ns = p.parse_args(args)
    append_decisions(ns.project, ns.stage, ns.decisions_file)
    print(f"OK: logged decisions for {ns.stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты — убедиться что PASS**

```bash
python -m pytest tests/test_log_decisions.py -v
```

Ожидаем: 6 тестов PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/log-decisions.py tests/test_log_decisions.py
git commit -m "feat(b28): add log-decisions.py for decisions.log.md tracking"
```

---

## Task 2: Обновить `brand-architect.md` — routing правок + протокол отклонений (B27+B28)

**Files:**
- Modify: `agents/brand-architect.md`

- [ ] **Step 1: Добавить секцию routing правок**

В `agents/brand-architect.md` после секции `## Process` добавить:

```markdown
## Routing правок от менеджера

При получении любой правки после показа `brand-kit.html` — определи тип:

**Концептуальные правки** (цвет, mood, стиль, "хочу светлее/темнее/другое направление"):
Ключевые слова: фон, background, цвет, colour, color, темнее, светлее, настроение, mood, стиль, style, характер, акцент, другой концепт.

→ STOP. Ответь:
```
⚠️ Это концептуальная правка — она затрагивает visual-concept.yaml.

Чтобы изменить [цвет / mood / палитру]:
1. Открой `03b_КОНЦЕПТ/visual-concept.yaml`
2. Внеси правку
3. Запусти `/landing-brand` снова — я перегенерирую brand-kit

Если хочешь — помогу сформулировать правку для visual-concept.yaml прямо сейчас.
```

**Локальные правки** (типографика, иконки, мелкие токены):
Ключевые слова: шрифт, font, типографика, иконки, icons, отступы, радиус, размер.

→ Принять правку прямо в 04, перегенерировать `brand-kit.md` + `brand-kit.html`, записать отклонение (см. ниже).

**Неоднозначно** → спроси: "Это правка по цвету/стилю или по шрифту/иконкам?"

## Протокол отклонений (B28)

По завершении этапа — перед approve — сформируй список решений принятых самостоятельно (не заданных в `visual-concept.yaml`):

Типичные отклонения на этапе 04:
- Конкретный шрифт (концепт задаёт направление, не название)
- Icon set (если не упомянут в концепте)
- Дополнительные токены (радиусы, motion, grid)

Если отклонения есть — напиши в чат:
```
✏️ Самостоятельные решения на этапе 04:
- [решение]: [обоснование]
```

И запиши в файл `<project>/.stage-decisions/04_brand.md`:
```
- [решение]: [обоснование]
```

Если отклонений нет — ничего не пишешь.
```

- [ ] **Step 2: Добавить `visual-concept.yaml` как обязательный input**

В секцию `## Inputs` добавить первой строкой:

```markdown
- `03b_КОНЦЕПТ/visual-concept.yaml` — **ОБЯЗАТЕЛЬНЫЙ**: утверждённый концепт (палитра, mood, типографическое направление). Агент реализует этот концепт, не выбирает палитру самостоятельно. Если файл отсутствует — STOP: "Сначала заверши этап 03b: `/landing-visual-concept`."
```

- [ ] **Step 3: Commit**

```bash
git add agents/brand-architect.md
git commit -m "feat(b27-b28): add routing rules and deviations protocol to brand-architect"
```

---

## Task 3: Обновить `design-system-generator.md` и `block-composer.md` — протокол отклонений (B28)

**Files:**
- Modify: `agents/design-system-generator.md`
- Modify: `agents/block-composer.md`

- [ ] **Step 1: Добавить протокол отклонений в `design-system-generator.md`**

В конец секции `## Process` (после последнего шага, перед approve) добавить:

```markdown
**Протокол отклонений (B28):**
По завершении этапа сформируй список самостоятельных решений не заданных в `visual-concept.yaml`.

Типичные отклонения на этапе 05:
- Дополнительные breakpoints
- Значения spacing/radius не упомянутые в концепте
- Motion tokens (easing, duration)

Если отклонения есть — напиши в чат:
```
✏️ Самостоятельные решения на этапе 05:
- [решение]: [обоснование]
```
И запиши в `<project>/.stage-decisions/05_design.md`.
Если нет — молчи.
```

- [ ] **Step 2: Добавить протокол отклонений в `block-composer.md`**

В конец секции `## Process` добавить:

```markdown
**Протокол отклонений (B28):**
По завершении этапа сформируй список самостоятельных решений не заданных в `visual-concept.yaml`.

Типичные отклонения на этапе 07b:
- Нестандартные отступы блоков
- Дополнительные декоративные элементы
- Изменения структуры блока относительно template.html

Если отклонения есть — напиши в чат:
```
✏️ Самостоятельные решения на этапе 07b:
- [решение]: [обоснование]
```
И запиши в `<project>/.stage-decisions/07b_composed.md`.
Если нет — молчи.
```

- [ ] **Step 3: Commit**

```bash
git add agents/design-system-generator.md agents/block-composer.md
git commit -m "feat(b28): add deviations protocol to design-system-generator and block-composer"
```

---

## Task 4: Обновить `landing-orchestrator.md` — вызов `log-decisions.py` после approve (B28)

**Files:**
- Modify: `agents/landing-orchestrator.md`

- [ ] **Step 1: Найти место вызова `gate-check --approve` в оркестраторе**

```bash
grep -n "approve\|gate-check" "D:\AI_TEAMS\landing_system\agents\landing-orchestrator.md" | head -20
```

- [ ] **Step 2: Добавить вызов `log-decisions.py` после каждого `--approve`**

В секцию `### Шаг 4 — Verify → approve → следующий` (или аналогичную) после строки с `gate-check.sh --approve` добавить:

```markdown
3. После approve — запустить:
   ```bash
   python scripts/log-decisions.py \
     --project <project> \
     --stage <stage> \
     --decisions-file <project>/.stage-decisions/<stage>.md
   ```
   Это дописывает отклонения агента в `decisions.log.md` (или запись "нет отклонений" если файла нет).
```

- [ ] **Step 3: Добавить `.stage-decisions/` в `.gitignore` template**

```bash
echo ".stage-decisions/" >> "D:\AI_TEAMS\landing_system\template\.gitignore"
```

Если `.gitignore` не существует:
```bash
echo ".stage-decisions/" > "D:\AI_TEAMS\landing_system\template\.gitignore"
```

- [ ] **Step 4: Commit**

```bash
git add agents/landing-orchestrator.md template/.gitignore
git commit -m "feat(b28): orchestrator calls log-decisions.py after each stage approve"
```

---

## Self-Review

**Spec coverage B27:**
- ✅ Routing концептуальных правок → возврат в 03b → Task 2
- ✅ Routing локальных правок → прямо в 04 → Task 2
- ✅ Неоднозначные правки → уточняющий вопрос → Task 2
- ✅ Сообщение менеджеру при концептуальной правке → Task 2

**Spec coverage B28:**
- ✅ `log-decisions.py` скрипт → Task 1
- ✅ Протокол отклонений в brand-architect → Task 2
- ✅ Протокол отклонений в design-system-generator → Task 3
- ✅ Протокол отклонений в block-composer → Task 3
- ✅ Оркестратор вызывает log-decisions.py → Task 4
- ✅ `.stage-decisions/` в gitignore → Task 4
- ✅ `decisions.log.md` формат → Task 1

**Placeholder scan:** нет TBD/TODO.

**Type consistency:** `append_decisions(project, stage, decisions_file)` — сигнатура совпадает в тестах и реализации. Путь `.stage-decisions/<stage>.md` совпадает в агентах и скрипте.
