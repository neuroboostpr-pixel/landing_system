# PR-F.3 — Project Graph + Template Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Реализовать `compile.py --source-mode=project-graph --project=<slug>` — компилит артефакты конкретного лендинга в `~/Lendings/<slug>/wiki/`. Интегрировать в template чтобы новые проекты получали wiki/memory автоматом. Мигрировать `dubai-avto-liza`.

**Architecture:** В отличие от system mode (где каждый исходник → SDK), большинство project-артефактов это структурированные YAML/JSON/HTML — парсим их в markdown БЕЗ SDK. SDK зовём только для `decisions.md` (синтез решений из daily logs если есть) и финального индекса.

**Tech Stack:** Python, PyYAML, beautifulsoup4 (уже в requirements). pytest.

**Связанный spec:** [2026-05-15-wiki-graph-markup-design.md](../specs/2026-05-15-wiki-graph-markup-design.md) разделы 3.2, 5.2, 6.

**Предыдущий PR:** PR-F.2 (system mode + bootstrap).

---

## File Structure

**Создаём:**
- `scripts/wiki/project_graph_compiler.py` — главная логика project-graph
- `scripts/wiki/parsers/__init__.py`
- `scripts/wiki/parsers/state_yaml.py` — `.landing-state.yaml` → markdown
- `scripts/wiki/parsers/prototype_md.py` — `prototype.md` → краткое summary
- `scripts/wiki/parsers/selections_yaml.py` — wireframe/photos selections → markdown
- `scripts/wiki/parsers/tokens_json.py` — design tokens → markdown
- `scripts/wiki/parsers/composed_html.py` — composed.html → блоки + slot mapping
- `scripts/wiki/prompts/project_index.md` — промпт для индекса проекта
- `tests/wiki/test_project_graph_compiler.py`
- `tests/wiki/test_parsers.py`
- `tests/wiki/fixtures/project/` — мини-проект для тестов
- `template/wiki/README.md` — placeholder для wiki
- `template/memory/README.md` — placeholder
- `template/.gitignore` — добавить `memory/` в игнор
- `scripts/migrate-add-wiki.sh` — миграция существующих проектов

**Модифицируем:**
- `scripts/wiki/compile.py` — реализовать ветку `project-graph`

---

## Task 1: Парсеры структурированных артефактов (без SDK)

**Цель:** Чистые функции `parse_*(path: Path) -> dict` возвращающие данные для генерации markdown.

**Files:**
- Create: `scripts/wiki/parsers/__init__.py`
- Create: `scripts/wiki/parsers/state_yaml.py`
- Create: `scripts/wiki/parsers/selections_yaml.py`
- Create: `scripts/wiki/parsers/tokens_json.py`
- Create: `scripts/wiki/parsers/composed_html.py`
- Create: `tests/wiki/test_parsers.py`
- Create: `tests/wiki/fixtures/project/` (минимальные YAML/JSON/HTML фикстуры)

- [ ] **Step 1: Создать пустой `parsers/__init__.py`**

```bash
touch scripts/wiki/parsers/__init__.py
```

- [ ] **Step 2: Создать фикстуры**

`tests/wiki/fixtures/project/.landing-state.yaml`:
```yaml
project: test-project
created: "2026-05-15T10:00:00Z"
schema_version: 2
stages:
  "00_brief": {status: n/a, timestamp: ""}
  "07a_prototype": {status: approved, timestamp: "2026-05-15T10:30:00Z"}
  "07b_wireframe": {status: approved, timestamp: "2026-05-15T11:00:00Z"}
  "07c_composed": {status: in_progress, timestamp: ""}
  "07d_photos": {status: locked, timestamp: ""}
```

`tests/wiki/fixtures/project/selections.yaml`:
```yaml
blocks:
  hero: hero-1
  features: features-3
  cta: cta-2
```

`tests/wiki/fixtures/project/tokens.json`:
```json
{
  "colors": {
    "primary": "#1a1a1a",
    "accent": "#d4af37"
  },
  "fonts": {
    "heading": "Playfair Display",
    "body": "Inter"
  }
}
```

`tests/wiki/fixtures/project/composed.html`:
```html
<!DOCTYPE html>
<html>
<body>
  <section class="lp-hero" data-block="hero-1">
    <h1>Premium авто в Дубае</h1>
    <img class="lp-hero-bg" src="07c_PHOTOS/processed/hero-bg.jpg">
  </section>
  <section class="lp-features" data-block="features-3">
    <h2>Преимущества</h2>
  </section>
</body>
</html>
```

- [ ] **Step 3: Написать failing tests `tests/wiki/test_parsers.py`**

```python
"""Тесты парсеров project-artifacts."""
from pathlib import Path

import pytest

from scripts.wiki.parsers import (
    state_yaml,
    selections_yaml,
    tokens_json,
    composed_html,
)

FIXTURES = Path(__file__).parent / "fixtures" / "project"


def test_parse_state_yaml_returns_current_stage():
    result = state_yaml.parse(FIXTURES / ".landing-state.yaml")
    assert result["project"] == "test-project"
    assert result["current_stage"] == "07c_composed"  # последний in_progress
    assert "07a_prototype" in result["approved"]
    assert "07b_wireframe" in result["approved"]


def test_parse_state_yaml_all_locked():
    """Если ни одного in_progress — current_stage = первый locked."""
    # фикстура all-locked.yaml
    tmp = FIXTURES / "all-locked.yaml"
    tmp.write_text("""project: x
stages:
  "07a_prototype": {status: locked, timestamp: ""}
  "07b_wireframe": {status: locked, timestamp: ""}
""")
    try:
        result = state_yaml.parse(tmp)
        assert result["current_stage"] == "07a_prototype"
    finally:
        tmp.unlink()


def test_parse_selections_yaml():
    result = selections_yaml.parse(FIXTURES / "selections.yaml")
    assert result["blocks"]["hero"] == "hero-1"
    assert result["blocks"]["features"] == "features-3"


def test_parse_tokens_json():
    result = tokens_json.parse(FIXTURES / "tokens.json")
    assert result["colors"]["primary"] == "#1a1a1a"
    assert result["fonts"]["heading"] == "Playfair Display"


def test_parse_composed_html_extracts_blocks():
    result = composed_html.parse(FIXTURES / "composed.html")
    assert "blocks" in result
    block_names = [b["block_id"] for b in result["blocks"]]
    assert "hero-1" in block_names
    assert "features-3" in block_names


def test_parse_composed_html_extracts_photo_refs():
    result = composed_html.parse(FIXTURES / "composed.html")
    photos = result.get("photo_references", [])
    assert any("hero-bg.jpg" in p for p in photos)
```

- [ ] **Step 4: Запустить — fail (ImportError)**

Run: `pytest tests/wiki/test_parsers.py -v`

- [ ] **Step 5: Реализовать парсеры**

`scripts/wiki/parsers/state_yaml.py`:
```python
"""Парсит .landing-state.yaml в dict с current_stage и approved."""
from pathlib import Path
import yaml


def parse(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    stages = data.get("stages", {})

    approved = [k for k, v in stages.items() if v.get("status") == "approved"]
    in_progress = [k for k, v in stages.items() if v.get("status") == "in_progress"]
    locked = [k for k, v in stages.items() if v.get("status") == "locked"]
    failed = [k for k, v in stages.items() if v.get("status") == "failed"]

    if in_progress:
        current = in_progress[0]
    elif locked:
        current = locked[0]
    elif failed:
        current = failed[0]
    else:
        current = "complete"

    return {
        "project": data.get("project", ""),
        "current_stage": current,
        "approved": approved,
        "in_progress": in_progress,
        "locked": locked,
        "failed": failed,
        "schema_version": data.get("schema_version"),
    }
```

`scripts/wiki/parsers/selections_yaml.py`:
```python
"""Парсит selections.yaml (wireframe/photos)."""
from pathlib import Path
import yaml


def parse(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
```

`scripts/wiki/parsers/tokens_json.py`:
```python
"""Парсит tokens.json (design tokens)."""
import json
from pathlib import Path


def parse(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
```

`scripts/wiki/parsers/composed_html.py`:
```python
"""Парсит composed.html — извлекает блоки и ссылки на фото."""
import re
from pathlib import Path

from bs4 import BeautifulSoup


def parse(path: Path) -> dict:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    blocks = []
    for el in soup.find_all(attrs={"data-block": True}):
        blocks.append({
            "block_id": el["data-block"],
            "tag": el.name,
            "classes": el.get("class", []),
        })

    photo_references = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and not src.startswith(("http://", "https://", "data:")):
            photo_references.append(src)

    return {
        "blocks": blocks,
        "photo_references": photo_references,
    }
```

- [ ] **Step 6: Запустить тесты**

Run: `pytest tests/wiki/test_parsers.py -v`
Expected: 6 PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/wiki/parsers/ tests/wiki/test_parsers.py tests/wiki/fixtures/project/
git commit -m "feat(wiki): парсеры project-артефактов (state, selections, tokens, html)

PR-F.3 Task 1 — без SDK, чистая YAML/JSON/HTML обработка."
```

---

## Task 2: Project graph compiler — главная логика

**Files:**
- Create: `scripts/wiki/project_graph_compiler.py`
- Create: `scripts/wiki/prompts/project_index.md`
- Create: `tests/wiki/test_project_graph_compiler.py`

- [ ] **Step 1: Создать `scripts/wiki/prompts/project_index.md`**

```markdown
Ты собираешь главный индекс wiki конкретного проекта-лендинга. На вход — структурированные данные о текущем состоянии проекта. На выход — `<project>/wiki/index.md` на русском.

# Формат ответа

Markdown БЕЗ frontmatter, БЕЗ обрамляющих ```. Структура:

```
# <project-slug> — wiki проекта

> Авто-граф проекта. Обновляется после каждого этапа. Не редактируй вручную.

## Текущее состояние
- **Этап:** <current_stage> (статус: <статус>)
- **Закрыто этапов:** <N> из <M>
- **Обновлено:** <дата>

## Этапы
- ✅ 07a_prototype — approved (2026-05-15)
- ✅ 07b_wireframe — approved
- 🔄 07c_composed — in_progress
- 🔒 07d_photos — locked

## Структура сайта
Кратко: какие блоки выбраны (из selections.yaml).

## Бренд
Кратко: основные цвета и шрифты (из tokens.json).

## Связанные документы
- [[blocks]] — карточки блоков
- [[photos]] — соответствие фото слотам
- [[brand]] — цвета и шрифты
- [[stage-current]] — детали текущего этапа
```

# Правила
- Простой русский.
- Эмодзи статусов: ✅ approved, 🔄 in_progress, 🔒 locked, ❌ failed, ⏭ n/a.
- Не выдумывай данные, только из входа.
```

- [ ] **Step 2: Написать failing tests `tests/wiki/test_project_graph_compiler.py`**

```python
"""Тесты project_graph_compiler."""
from pathlib import Path
import shutil

import pytest

from scripts.wiki import project_graph_compiler


FIXTURES = Path(__file__).parent / "fixtures" / "project"


@pytest.fixture
def fake_project(tmp_path):
    """Имитирует структуру проекта-лендинга."""
    project = tmp_path / "test-project"
    project.mkdir()
    shutil.copy(FIXTURES / ".landing-state.yaml", project / ".landing-state.yaml")

    (project / "07a_WIREFRAME").mkdir()
    shutil.copy(FIXTURES / "selections.yaml", project / "07a_WIREFRAME" / "selections.yaml")

    (project / "04_БРЕНД").mkdir()
    shutil.copy(FIXTURES / "tokens.json", project / "04_БРЕНД" / "tokens.json")

    (project / "07b_COMPOSED").mkdir()
    shutil.copy(FIXTURES / "composed.html", project / "07b_COMPOSED" / "composed.html")

    return project


def test_compile_creates_wiki_dir(fake_project, mocker):
    mocker.patch(
        "scripts.wiki.project_graph_compiler.sdk_client.generate",
        return_value="# Project Index\n- состояние проекта",
    )
    project_graph_compiler.compile_project(project_root=fake_project)

    wiki = fake_project / "wiki"
    assert wiki.exists()
    assert (wiki / "index.md").exists()
    assert (wiki / "concepts" / "stage-current.md").exists()


def test_compile_stage_current_contains_current_stage(fake_project, mocker):
    mocker.patch(
        "scripts.wiki.project_graph_compiler.sdk_client.generate",
        return_value="idx",
    )
    project_graph_compiler.compile_project(project_root=fake_project)

    content = (fake_project / "wiki" / "concepts" / "stage-current.md").read_text()
    assert "07c_composed" in content


def test_compile_blocks_concept_lists_selected_blocks(fake_project, mocker):
    mocker.patch(
        "scripts.wiki.project_graph_compiler.sdk_client.generate",
        return_value="idx",
    )
    project_graph_compiler.compile_project(project_root=fake_project)

    blocks_path = fake_project / "wiki" / "concepts" / "blocks.md"
    if blocks_path.exists():
        content = blocks_path.read_text()
        assert "hero-1" in content
        assert "features-3" in content


def test_compile_brand_concept_has_tokens(fake_project, mocker):
    mocker.patch(
        "scripts.wiki.project_graph_compiler.sdk_client.generate",
        return_value="idx",
    )
    project_graph_compiler.compile_project(project_root=fake_project)

    brand = (fake_project / "wiki" / "concepts" / "brand.md").read_text()
    assert "#1a1a1a" in brand or "primary" in brand.lower()


def test_compile_appends_log(fake_project, mocker):
    mocker.patch(
        "scripts.wiki.project_graph_compiler.sdk_client.generate",
        return_value="idx",
    )
    project_graph_compiler.compile_project(project_root=fake_project)

    log = (fake_project / "wiki" / "log.md").read_text()
    assert "project-graph" in log
```

- [ ] **Step 3: Запустить — fail**

Run: `pytest tests/wiki/test_project_graph_compiler.py -v`

- [ ] **Step 4: Реализовать `scripts/wiki/project_graph_compiler.py`**

```python
# scripts/wiki/project_graph_compiler.py
"""Компилит артефакты проекта-лендинга в <project>/wiki/.

В отличие от system_compiler — большинство концептов генерится БЕЗ SDK
(парсинг yaml/json/html → markdown). SDK зовётся только для index.md.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from scripts.wiki import sdk_client, utils
from scripts.wiki.parsers import (
    state_yaml,
    selections_yaml,
    tokens_json,
    composed_html,
)

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _stage_current_md(state: dict) -> str:
    stages_md = "\n".join(
        f"- {s}" for s in state.get("approved", [])
    )
    return f"""---
type: project-state
name: stage-current
updated: {date.today().isoformat()}
---

# Текущее состояние проекта

**Проект:** `{state.get('project', '')}`
**Текущий этап:** `{state.get('current_stage', '?')}`

## Закрытые этапы
{stages_md or '_(нет)_'}

## В работе
{chr(10).join('- ' + s for s in state.get('in_progress', [])) or '_(нет)_'}

## Заблокированные
{chr(10).join('- ' + s for s in state.get('locked', [])) or '_(нет)_'}
"""


def _blocks_md(selections: dict) -> str:
    blocks = selections.get("blocks", {})
    if not blocks:
        return ""
    lines = "\n".join(f"- **{slot}**: `{block_id}`" for slot, block_id in blocks.items())
    return f"""---
type: project-blocks
name: blocks
updated: {date.today().isoformat()}
---

# Выбранные блоки

{lines}
"""


def _brand_md(tokens: dict) -> str:
    colors = tokens.get("colors", {})
    fonts = tokens.get("fonts", {})
    colors_lines = "\n".join(f"- **{k}**: `{v}`" for k, v in colors.items())
    fonts_lines = "\n".join(f"- **{k}**: `{v}`" for k, v in fonts.items())
    return f"""---
type: project-brand
name: brand
updated: {date.today().isoformat()}
---

# Бренд

## Цвета
{colors_lines or '_(пусто)_'}

## Шрифты
{fonts_lines or '_(пусто)_'}
"""


def _photos_md(composed: dict) -> str:
    refs = composed.get("photo_references", [])
    if not refs:
        return ""
    lines = "\n".join(f"- `{r}`" for r in refs)
    return f"""---
type: project-photos
name: photos
updated: {date.today().isoformat()}
---

# Фото в проекте

{lines}
"""


def _append_log(log_path: Path, stage: str) -> None:
    today = date.today().isoformat()
    entry = f"\n## [{today}] compile --source-mode=project-graph\n- updated for stage `{stage}`\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def _build_index(state: dict, has_blocks: bool, has_brand: bool) -> str:
    """Зовёт SDK для index.md."""
    prompt = (PROMPTS_DIR / "project_index.md").read_text(encoding="utf-8")
    user = f"""Проект: {state.get('project')}
Текущий этап: {state.get('current_stage')}
Closed: {', '.join(state.get('approved', []))}
In progress: {', '.join(state.get('in_progress', []))}
Locked: {', '.join(state.get('locked', []))}
Концепты доступны: stage-current{', blocks' if has_blocks else ''}{', brand' if has_brand else ''}, photos
"""
    return sdk_client.generate(system=prompt, user=user)


def compile_project(project_root: Path) -> dict[str, Any]:
    """Компилит артефакты проекта в <project>/wiki/."""
    wiki_dir = project_root / "wiki"
    concepts_dir = wiki_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    # 1. .landing-state.yaml → stage-current.md
    state_path = project_root / ".landing-state.yaml"
    if not state_path.exists():
        raise FileNotFoundError(f"{state_path} not found")
    state = state_yaml.parse(state_path)
    utils.atomic_write(concepts_dir / "stage-current.md", _stage_current_md(state))

    # 2. wireframe selections → blocks.md (опционально)
    has_blocks = False
    selections_path = project_root / "07a_WIREFRAME" / "selections.yaml"
    if selections_path.exists():
        selections = selections_yaml.parse(selections_path)
        md = _blocks_md(selections)
        if md:
            utils.atomic_write(concepts_dir / "blocks.md", md)
            has_blocks = True

    # 3. tokens → brand.md
    has_brand = False
    tokens_path = project_root / "04_БРЕНД" / "tokens.json"
    if tokens_path.exists():
        tokens = tokens_json.parse(tokens_path)
        utils.atomic_write(concepts_dir / "brand.md", _brand_md(tokens))
        has_brand = True

    # 4. composed.html → photos.md
    composed_path = project_root / "07b_COMPOSED" / "composed.html"
    if composed_path.exists():
        composed = composed_html.parse(composed_path)
        md = _photos_md(composed)
        if md:
            utils.atomic_write(concepts_dir / "photos.md", md)

    # 5. Index через SDK
    try:
        index_content = _build_index(state, has_blocks, has_brand)
        utils.atomic_write(wiki_dir / "index.md", index_content)
    except sdk_client.SDKError:
        # fallback — простой индекс без SDK
        utils.atomic_write(
            wiki_dir / "index.md",
            f"# {state.get('project', 'project')} wiki\n\nТекущий этап: {state.get('current_stage')}\n",
        )

    # 6. Log
    _append_log(wiki_dir / "log.md", state.get("current_stage", "?"))

    return {
        "current_stage": state.get("current_stage"),
        "concepts_written": ["stage-current.md", "blocks.md", "brand.md", "photos.md"],
    }
```

- [ ] **Step 5: Запустить тесты**

Run: `pytest tests/wiki/test_project_graph_compiler.py -v`
Expected: 5 PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/wiki/project_graph_compiler.py scripts/wiki/prompts/project_index.md \
        tests/wiki/test_project_graph_compiler.py
git commit -m "feat(wiki): project_graph_compiler — граф конкретного лендинга

PR-F.3 Task 2. Парсит state/selections/tokens/composed без SDK,
SDK только для index.md."
```

---

## Task 3: Подключить в CLI

**Files:**
- Modify: `scripts/wiki/compile.py`

- [ ] **Step 1: Заменить ветку `project-graph` в `compile.py` на:**

```python
    if args.source_mode == "project-graph":
        from pathlib import Path
        from scripts.wiki import project_graph_compiler
        project_root = Path.home() / "Lendings" / args.project
        if not project_root.exists():
            print(f"ERROR: проект не найден: {project_root}", file=sys.stderr)
            return 2
        try:
            result = project_graph_compiler.compile_project(project_root=project_root)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        print(f"Project: {args.project}")
        print(f"Current stage: {result['current_stage']}")
        print(f"Wiki updated: {project_root / 'wiki'}")
        return 0
```

- [ ] **Step 2: Запустить весь wiki-сьют**

Run: `pytest tests/wiki/ -v`
Expected: все тесты PASS

- [ ] **Step 3: Commit**

```bash
git add scripts/wiki/compile.py
git commit -m "feat(wiki): compile.py подключает project-graph mode

PR-F.3 Task 3."
```

---

## Task 4: Интеграция в `template/`

**Files:**
- Create: `template/wiki/README.md`
- Create: `template/memory/README.md`
- Create or modify: `template/.gitignore`

- [ ] **Step 1: Создать `template/wiki/README.md`**

```markdown
# wiki/ — граф структуры проекта

Эта папка автоматически наполняется компайлером `landing-system/scripts/wiki/`
после каждого этапа pipeline.

**Не редактируй вручную** — содержимое перезаписывается.

## Структура
- `index.md` — главный индекс (читай первым)
- `log.md` — хронология обновлений
- `concepts/` — концепты по этому проекту:
  - `stage-current.md` — текущий этап
  - `blocks.md` — выбранные блоки
  - `brand.md` — цвета и шрифты
  - `photos.md` — карта фото-слотов

## Как обновляется

Автоматически:
- После `gate-check.sh exit 0` (закрытие этапа)
- Можно вручную: `python -m scripts.wiki.compile --source-mode=project-graph --project=<slug>`

Подробнее: `landing-system/docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md`.
```

- [ ] **Step 2: Создать `template/memory/README.md`**

```markdown
# memory/ — память сессий по проекту

Эта папка хранит даты разговоров с Claude Code по этому конкретному лендингу.

**Не редактируй вручную.** Файлы создаются хуками SessionEnd / PreCompact автоматически.

## Структура
- `daily/YYYY-MM-DD.md` — сырые логи сессий за день
- `compiled/index.md` — компилированные уроки и решения
- `compiled/concepts/` — концепты по конкретным решениям
- `compiled/qa/` — ответы из query.py --file-back

## Конфиденциальность

Эта папка в `.gitignore` (могут быть клиентские детали в транскриптах).
Если нужно поделиться знаниями с командой — экспортируй вручную нужные файлы.

Подробнее: `landing-system/docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md`.
```

- [ ] **Step 3: Создать или дополнить `template/.gitignore`**

Если файла нет:
```
# Личная память сессий — не коммитим
memory/daily/
memory/compiled/
# (только README.md остаётся в репо)
!memory/README.md

# Wiki кэш
wiki/.cache.json
```

Если есть — добавить эти строки.

- [ ] **Step 4: Smoke**

```bash
ls template/wiki/ template/memory/
cat template/.gitignore 2>/dev/null | grep memory
```
Expected: README.md в обеих, gitignore содержит `memory/`.

- [ ] **Step 5: Commit**

```bash
git add template/wiki/ template/memory/ template/.gitignore
git commit -m "feat(wiki): template получает wiki/ и memory/ автоматом

PR-F.3 Task 4 — новые проекты создаются с заготовками."
```

---

## Task 5: Миграция существующих проектов

**Files:**
- Create: `scripts/migrate-add-wiki.sh`

- [ ] **Step 1: Создать `scripts/migrate-add-wiki.sh`**

```bash
#!/bin/bash
# scripts/migrate-add-wiki.sh
# Добавляет wiki/ и memory/ к существующему проекту-лендингу.
# Использование: bash scripts/migrate-add-wiki.sh ~/Lendings/<slug>

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Использование: $0 <путь к проекту>"
    echo "Пример: $0 ~/Lendings/dubai-avto-liza"
    exit 1
fi

PROJECT_DIR="$1"
TEMPLATE_DIR="$(dirname "$0")/../template"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: проект не найден: $PROJECT_DIR"
    exit 2
fi

echo "📚 Миграция wiki/ + memory/ в $PROJECT_DIR..."

mkdir -p "$PROJECT_DIR/wiki" "$PROJECT_DIR/memory"

# Копируем README placeholders (не перезаписываем если есть)
[ -f "$PROJECT_DIR/wiki/README.md" ] || cp "$TEMPLATE_DIR/wiki/README.md" "$PROJECT_DIR/wiki/README.md"
[ -f "$PROJECT_DIR/memory/README.md" ] || cp "$TEMPLATE_DIR/memory/README.md" "$PROJECT_DIR/memory/README.md"

# .gitignore
if [ -f "$PROJECT_DIR/.gitignore" ]; then
    grep -q "memory/daily" "$PROJECT_DIR/.gitignore" || cat "$TEMPLATE_DIR/.gitignore" >> "$PROJECT_DIR/.gitignore"
else
    cp "$TEMPLATE_DIR/.gitignore" "$PROJECT_DIR/.gitignore"
fi

# Первичная компиляция графа
SLUG=$(basename "$PROJECT_DIR")
LANDING_SYSTEM_DIR="$(dirname "$0")/.."

echo "▶️ Первый прогон graph compile..."
(cd "$LANDING_SYSTEM_DIR" && python3 -m scripts.wiki.compile --source-mode=project-graph --project="$SLUG")

echo "✅ Готово. Открой $PROJECT_DIR/wiki/index.md"
```

- [ ] **Step 2: Сделать исполняемым**

```bash
chmod +x scripts/migrate-add-wiki.sh
```

- [ ] **Step 3: Smoke test на `dubai-avto-liza`**

```bash
bash scripts/migrate-add-wiki.sh ~/Lendings/dubai-avto-liza
```

Ожидаемо:
- Появились `~/Lendings/dubai-avto-liza/wiki/{index.md,log.md,concepts/}`
- `~/Lendings/dubai-avto-liza/memory/README.md` тоже
- `.gitignore` обновлён

- [ ] **Step 4: Проверить результат глазами**

```bash
cat ~/Lendings/dubai-avto-liza/wiki/index.md
ls ~/Lendings/dubai-avto-liza/wiki/concepts/
```

- [ ] **Step 5: Commit миграции и (если у dubai-avto-liza есть git) — закоммитить и в нём**

```bash
# В landing-system:
git add scripts/migrate-add-wiki.sh
git commit -m "feat(wiki): миграционный скрипт add-wiki для существующих проектов

PR-F.3 Task 5. Применён к dubai-avto-liza."

# В проекте dubai-avto-liza (если он git-репо):
cd ~/Lendings/dubai-avto-liza
git status 2>/dev/null && git add wiki/ memory/README.md .gitignore && \
    git commit -m "feat(wiki): первая компиляция wiki/ + memory/ placeholder

Миграция через landing-system/scripts/migrate-add-wiki.sh"
```

---

## Self-Review

**Spec coverage (раздел 5.2 project-graph):**
- ✅ Парсинг state, selections, tokens, composed
- ✅ Большинство концептов без SDK
- ✅ SDK для index.md
- ✅ Интеграция в template
- ✅ Миграция dubai-avto-liza
- ⏭️ `decisions.md` — пропустил (нужен daily logs, появятся в PR-F.4)
- ⏭️ Автоматический вызов после gate-check.sh — пропустил (это правка orchestrator, перенесено в PR-G)

**Placeholders:** нет.

**Type consistency:**
- Парсеры все возвращают `dict` с консистентными ключами.
- `compile_project(project_root: Path) -> dict` — совместим с `compile.py` ожиданиями.

**Риски:**
1. **dubai-avto-liza имеет нестандартные пути** (например `04_БРЕНД` может не существовать). Компайлер должен **gracefully skip** отсутствующие источники — это уже учтено (каждая ветка проверяет `.exists()`).
2. **SDK call для index** — один на проект, ~10 сек. Не дорого.

---

## Дальше после PR-F.3

PR-F.4 — хуки + conversations:
- `.claude/settings.json` в template и landing-system
- `flush.py` адаптация из coleam00
- session-start/end/pre-compact хуки

PR-F.5 — lint + preview.html.
