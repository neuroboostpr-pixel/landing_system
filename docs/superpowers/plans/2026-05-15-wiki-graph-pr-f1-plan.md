# PR-F.1 — Wiki Infrastructure (фундамент) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Поставить инфраструктуру `scripts/wiki/` (порт coleam00) в landing-system: конфиг, утилиты, CLI-скелет компайлера. БЕЗ логики компиляции — её добавляем в PR-F.2.

**Architecture:** Python-модуль `scripts/wiki/` с конфигом для трёх source-mode и CLI на argparse. Тесты на pytest (как уже принято в landing-system). Никаких внешних вызовов SDK на этом PR — только заготовка.

**Tech Stack:** Python 3.11+, pytest, PyYAML (уже в requirements.txt). `claude-agent-sdk` добавится в PR-F.2.

**Связанный spec:** [2026-05-15-wiki-graph-markup-design.md](../specs/2026-05-15-wiki-graph-markup-design.md)

---

## File Structure

**Создаём:**
- `scripts/wiki/__init__.py` — пустой, делает модулем
- `scripts/wiki/config.py` — пути и source-mode определения
- `scripts/wiki/utils.py` — хелперы: frontmatter read/write, atomic write, kebab-case slug
- `scripts/wiki/compile.py` — CLI entry point (argparse + диспатчер по source-mode, без логики)
- `scripts/wiki/README.md` — короткое объяснение что это
- `tests/wiki/__init__.py`
- `tests/wiki/test_config.py`
- `tests/wiki/test_utils.py`
- `tests/wiki/test_compile_cli.py`

**Модифицируем:**
- `requirements.txt` — пока ничего не добавляем (PyYAML уже есть)
- `CLAUDE.md` — добавить упоминание `scripts/wiki/` в разделе «Структура»

**НЕ трогаем на этом PR:**
- хуки `.claude/settings.json` — будут в PR-F.4
- `template/` — будет в PR-F.3
- `compile.py` логика — будет в PR-F.2

---

## Task 1: Создать тесты конфига (TDD)

**Files:**
- Create: `tests/wiki/__init__.py`
- Create: `tests/wiki/test_config.py`

- [ ] **Step 1: Создать пустой `tests/wiki/__init__.py`**

```bash
touch "tests/wiki/__init__.py"
```

- [ ] **Step 2: Написать failing test `test_config.py`**

```python
# tests/wiki/test_config.py
"""Тесты для wiki/config.py — определения путей и source-mode."""
import pytest
from pathlib import Path
from scripts.wiki import config


def test_source_modes_defined():
    """Должны быть определены три режима: system, project-graph, conversations."""
    assert "system" in config.SOURCE_MODES
    assert "project-graph" in config.SOURCE_MODES
    assert "conversations" in config.SOURCE_MODES


def test_system_sources_list():
    """SYSTEM_SOURCES — список словарей с ключами path, concept_dir."""
    assert isinstance(config.SYSTEM_SOURCES, list)
    assert len(config.SYSTEM_SOURCES) >= 5  # agents, skills, commands, template, standards
    for entry in config.SYSTEM_SOURCES:
        assert "path" in entry
        assert "concept_dir" in entry


def test_system_sources_include_expected_paths():
    """Проверка что в системных источниках есть основные категории."""
    paths = [e["path"] for e in config.SYSTEM_SOURCES]
    assert any("agents" in p for p in paths)
    assert any("skills" in p for p in paths)
    assert any("commands" in p for p in paths)
    assert any("template" in p for p in paths)
    assert any("standards" in p for p in paths)


def test_project_sources_list():
    """PROJECT_SOURCES — список с путями относительно корня проекта."""
    assert isinstance(config.PROJECT_SOURCES, list)
    paths = [e["path"] for e in config.PROJECT_SOURCES]
    assert any(".landing-state.yaml" in p for p in paths)
    assert any("07_ПРОТОТИП" in p for p in paths)
    assert any("04_БРЕНД" in p for p in paths)


def test_repo_root_resolves_to_landing_system():
    """REPO_ROOT — корень landing-system, относительно которого считаются пути."""
    assert isinstance(config.REPO_ROOT, Path)
    assert config.REPO_ROOT.name == "landing-system"
    assert (config.REPO_ROOT / "agents").exists()


def test_wiki_dir_inside_repo():
    """WIKI_DIR — landing-system/wiki/."""
    assert config.WIKI_DIR == config.REPO_ROOT / "wiki"
```

- [ ] **Step 3: Запустить test, убедиться что фейлится**

Run: `cd landing-system && pytest tests/wiki/test_config.py -v`
Expected: FAIL с `ModuleNotFoundError: No module named 'scripts.wiki'`

- [ ] **Step 4: Создать `scripts/wiki/__init__.py` и `scripts/wiki/config.py`**

```bash
touch "scripts/wiki/__init__.py"
```

```python
# scripts/wiki/config.py
"""Конфигурация wiki-компайлера.

Определяет источники для трёх режимов компиляции:
- system: компилит landing-system/{agents,skills,commands,template,docs/standards}
- project-graph: компилит артефакты конкретного лендинга (~/Lendings/<slug>/)
- conversations: компилит daily logs сессий в knowledge базу (coleam00 default)
"""
from pathlib import Path

# Корень landing-system — рассчитывается от расположения этого файла.
# scripts/wiki/config.py → корень = parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]

# Папка системного wiki внутри landing-system.
WIKI_DIR = REPO_ROOT / "wiki"

# Три режима компиляции.
SOURCE_MODES = ("system", "project-graph", "conversations")

# Источники для системного wiki.
# Каждая запись: glob-паттерн относительно REPO_ROOT + папка концептов в wiki/.
SYSTEM_SOURCES = [
    {"path": "agents/*.md", "concept_dir": "agents"},
    {"path": "skills/*/SKILL.md", "concept_dir": "skills"},
    {"path": "commands/*.md", "concept_dir": "commands"},
    {"path": "template/*/README.md", "concept_dir": "stages"},
    {"path": "docs/standards/*.md", "concept_dir": "rules"},
    {"path": "block-library/*/meta.yaml", "concept_dir": "blocks"},
]

# Источники для графа конкретного проекта (~/Lendings/<slug>/).
# Пути относительно корня проекта.
PROJECT_SOURCES = [
    {"path": ".landing-state.yaml", "concept": "stage-current.md"},
    {"path": "07_ПРОТОТИП/prototype.md", "concept": "prototype.md"},
    {"path": "07a_WIREFRAME/selections.yaml", "concept": "blocks.md"},
    {"path": "07b_COMPOSED/composed.html", "concept": "blocks.md"},
    {"path": "07c_PHOTOS/selections.yaml", "concept": "photos.md"},
    {"path": "04_БРЕНД/tokens.json", "concept": "brand.md"},
    {"path": "04_БРЕНД/brand-kit.md", "concept": "brand.md"},
]
```

- [ ] **Step 5: Запустить тесты, убедиться что прошли**

Run: `pytest tests/wiki/test_config.py -v`
Expected: PASS (6 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/wiki/__init__.py scripts/wiki/config.py tests/wiki/__init__.py tests/wiki/test_config.py
git commit -m "feat(wiki): добавить config.py с тремя source-mode

PR-F.1 Task 1 — определение путей и источников для wiki-компайлера.
Три режима: system, project-graph, conversations.

См. docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md"
```

---

## Task 2: Утилиты — frontmatter, atomic write, slug

**Files:**
- Create: `scripts/wiki/utils.py`
- Create: `tests/wiki/test_utils.py`

- [ ] **Step 1: Написать failing tests**

```python
# tests/wiki/test_utils.py
"""Тесты для wiki/utils.py."""
import pytest
from pathlib import Path
from scripts.wiki import utils


def test_slugify_basic():
    assert utils.slugify("Landing Orchestrator") == "landing-orchestrator"


def test_slugify_cyrillic():
    """Кириллица транслитерируется в латиницу для имён файлов."""
    assert utils.slugify("Финальная проверка") == "finalnaya-proverka"


def test_slugify_strip_special_chars():
    assert utils.slugify("Hero/Block: v2.0!") == "hero-block-v2-0"


def test_parse_frontmatter_present():
    """Парсит YAML frontmatter, возвращает (metadata, body)."""
    text = """---
type: agent
name: foo
---
Body text here.
"""
    meta, body = utils.parse_frontmatter(text)
    assert meta == {"type": "agent", "name": "foo"}
    assert body.strip() == "Body text here."


def test_parse_frontmatter_absent():
    """Если frontmatter нет — metadata пустой, body = весь текст."""
    text = "Just body, no frontmatter."
    meta, body = utils.parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_write_with_frontmatter(tmp_path):
    """Пишет файл с frontmatter и body."""
    path = tmp_path / "test.md"
    utils.write_with_frontmatter(
        path,
        metadata={"type": "agent", "name": "foo"},
        body="Body content.",
    )
    content = path.read_text()
    assert content.startswith("---\n")
    assert "type: agent" in content
    assert "Body content." in content


def test_atomic_write(tmp_path):
    """atomic_write не оставляет частичный файл при ошибке."""
    target = tmp_path / "out.md"
    utils.atomic_write(target, "hello")
    assert target.read_text() == "hello"
    # Перезапись
    utils.atomic_write(target, "world")
    assert target.read_text() == "world"
```

- [ ] **Step 2: Запустить тесты, увидеть failure**

Run: `pytest tests/wiki/test_utils.py -v`
Expected: FAIL с `ImportError` / `AttributeError`

- [ ] **Step 3: Реализовать `utils.py`**

```python
# scripts/wiki/utils.py
"""Утилиты для wiki: slug, frontmatter, atomic write."""
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import yaml

# Карта транслитерации кириллицы (упрощённая, для slug).
CYRILLIC_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str) -> str:
    """Превращает строку в kebab-case slug. Поддерживает кириллицу."""
    text = text.lower()
    text = "".join(CYRILLIC_MAP.get(ch, ch) for ch in text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Извлекает YAML frontmatter из markdown.

    Returns:
        (metadata, body). Если frontmatter нет — metadata={}, body=весь текст.
    """
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text
    return meta, parts[2]


def write_with_frontmatter(
    path: Path, metadata: dict[str, Any], body: str
) -> None:
    """Атомарно пишет markdown с frontmatter."""
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
    content = f"---\n{fm}---\n{body}"
    atomic_write(path, content)


def atomic_write(path: Path, content: str) -> None:
    """Атомарная запись через временный файл + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
```

- [ ] **Step 4: Запустить тесты, убедиться что прошли**

Run: `pytest tests/wiki/test_utils.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/utils.py tests/wiki/test_utils.py
git commit -m "feat(wiki): utils — slugify, frontmatter, atomic write

PR-F.1 Task 2 — базовые хелперы для wiki-компайлера."
```

---

## Task 3: CLI-скелет компайлера

**Files:**
- Create: `scripts/wiki/compile.py`
- Create: `tests/wiki/test_compile_cli.py`

- [ ] **Step 1: Написать failing tests для CLI**

```python
# tests/wiki/test_compile_cli.py
"""Тесты для CLI compile.py."""
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_compile(*args):
    """Запускает compile.py как подпроцесс."""
    return subprocess.run(
        [sys.executable, "-m", "scripts.wiki.compile", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_help_shows_source_mode():
    """`--help` показывает флаг --source-mode со всеми тремя режимами."""
    result = run_compile("--help")
    assert result.returncode == 0
    assert "--source-mode" in result.stdout
    assert "system" in result.stdout
    assert "project-graph" in result.stdout
    assert "conversations" in result.stdout


def test_requires_source_mode():
    """Без --source-mode CLI падает с понятной ошибкой."""
    result = run_compile()
    assert result.returncode != 0
    assert "source-mode" in (result.stderr + result.stdout).lower()


def test_invalid_source_mode():
    """Невалидный --source-mode → exit с ошибкой."""
    result = run_compile("--source-mode=invalid")
    assert result.returncode != 0


def test_system_mode_not_yet_implemented():
    """system mode принимается, но в PR-F.1 говорит что не реализован."""
    result = run_compile("--source-mode=system", "--dry-run")
    # В PR-F.1 — печатает stub, exit 0
    assert result.returncode == 0
    assert "not implemented" in (result.stdout + result.stderr).lower() or \
           "PR-F.2" in (result.stdout + result.stderr)


def test_project_graph_requires_project():
    """project-graph без --project → ошибка."""
    result = run_compile("--source-mode=project-graph")
    assert result.returncode != 0
    assert "project" in (result.stdout + result.stderr).lower()
```

- [ ] **Step 2: Запустить, увидеть failure**

Run: `pytest tests/wiki/test_compile_cli.py -v`
Expected: FAIL — модуль не существует

- [ ] **Step 3: Реализовать `compile.py` (CLI-скелет, без логики)**

```python
# scripts/wiki/compile.py
"""Wiki compiler CLI.

Три режима компиляции:
  --source-mode=system          компилит landing-system в landing-system/wiki/
  --source-mode=project-graph   компилит артефакты проекта в <project>/wiki/
                                требует --project=<slug>
  --source-mode=conversations   компилит daily logs сессий (coleam00 default)
                                требует --project=<slug>

В PR-F.1 — только скелет. Логика добавляется в PR-F.2 (system),
PR-F.3 (project-graph), PR-F.4 (conversations).
"""
import argparse
import sys

from scripts.wiki import config


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m scripts.wiki.compile",
        description="Wiki compiler — преобразует исходники в структурированную wiki.",
    )
    parser.add_argument(
        "--source-mode",
        required=True,
        choices=config.SOURCE_MODES,
        help="Что компилируем: system / project-graph / conversations",
    )
    parser.add_argument(
        "--project",
        help="Slug проекта (для project-graph и conversations)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Печатает план без записи файлов",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.source_mode in ("project-graph", "conversations") and not args.project:
        print(
            f"ERROR: --source-mode={args.source_mode} требует --project=<slug>",
            file=sys.stderr,
        )
        return 2

    if args.source_mode == "system":
        print("[PR-F.1] system mode принят (логика будет в PR-F.2, not implemented).")
        if args.dry_run:
            print(f"DRY RUN: целевая папка {config.WIKI_DIR}")
        return 0

    if args.source_mode == "project-graph":
        print(f"[PR-F.1] project-graph mode для {args.project} (логика в PR-F.3, not implemented).")
        return 0

    if args.source_mode == "conversations":
        print(f"[PR-F.1] conversations mode для {args.project} (логика в PR-F.4, not implemented).")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Запустить тесты**

Run: `pytest tests/wiki/test_compile_cli.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Запустить smoke test вручную**

Run: `cd landing-system && python -m scripts.wiki.compile --help`
Expected: usage с тремя source-mode

Run: `python -m scripts.wiki.compile --source-mode=system --dry-run`
Expected: `[PR-F.1] system mode принят...`

- [ ] **Step 6: Commit**

```bash
git add scripts/wiki/compile.py tests/wiki/test_compile_cli.py
git commit -m "feat(wiki): CLI-скелет compile.py с --source-mode

PR-F.1 Task 3 — argparse-скелет, три режима принимаются,
но логика будет в PR-F.2/F.3/F.4. Сейчас печатает stub."
```

---

## Task 4: README модуля + обновление CLAUDE.md

**Files:**
- Create: `scripts/wiki/README.md`
- Modify: `CLAUDE.md` (добавить упоминание)

- [ ] **Step 1: Создать `scripts/wiki/README.md`**

```markdown
# scripts/wiki — wiki compiler

Адаптация [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler) под нашу систему.

## Три режима

| Mode | Источник | Назначение |
|---|---|---|
| `system` | `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/`, `block-library/` | `landing-system/wiki/` — карта архитектуры |
| `project-graph` | артефакты проекта (`composed.html`, `selections.yaml`, …) | `~/Lendings/<slug>/wiki/` — граф структуры лендинга |
| `conversations` | транскрипты сессий | `~/Lendings/<slug>/memory/compiled/` — память разговоров |

## Использование

```bash
# Системный wiki (после изменений в системе)
python -m scripts.wiki.compile --source-mode=system

# Граф конкретного проекта
python -m scripts.wiki.compile --source-mode=project-graph --project=dubai-avto-liza

# Память разговоров (обычно вызывается хуком, не вручную)
python -m scripts.wiki.compile --source-mode=conversations --project=dubai-avto-liza
```

## Статус по PR

- **PR-F.1** (текущий): инфраструктура + CLI-скелет. Логика не реализована.
- **PR-F.2**: реализация `--source-mode=system`.
- **PR-F.3**: реализация `--source-mode=project-graph` + интеграция в `template/`.
- **PR-F.4**: хуки SessionStart/End/PreCompact + реализация `--source-mode=conversations`.
- **PR-F.5**: `lint.py` + `preview.html` рендерер.

Полный spec: [docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md](../../docs/superpowers/specs/2026-05-15-wiki-graph-markup-design.md)
```

- [ ] **Step 2: Дополнить `CLAUDE.md`**

Найти секцию `## Структура` (`Read landing-system/CLAUDE.md`), добавить строку:

```markdown
- `scripts/wiki/` — wiki-компайлер (3 режима: system / project-graph / conversations). См. `scripts/wiki/README.md`.
```

- [ ] **Step 3: Smoke-проверка что markdown валидный**

Run: `python -c "import scripts.wiki.compile; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Запустить весь тест-сьют `tests/wiki/`**

Run: `pytest tests/wiki/ -v`
Expected: все тесты pass (≥18 в сумме)

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/README.md CLAUDE.md
git commit -m "docs(wiki): README модуля + упоминание в CLAUDE.md

PR-F.1 Task 4 — документация. Завершает PR-F.1."
```

---

## Task 5: Финальная проверка + push

- [ ] **Step 1: Полный pytest**

Run: `pytest tests/wiki/ -v`
Expected: ≥18 tests pass, 0 fail

- [ ] **Step 2: Проверить git log**

Run: `git log --oneline -n 5`
Expected: 4 коммита PR-F.1

- [ ] **Step 3: Спросить пользователя про push**

> "PR-F.1 готов. 4 коммита. Сделать push в origin или сначала ревью?"

Ждать ответа. Если push — `git push origin <branch>`. Если ревью — остановиться.

---

## Self-Review

**Coverage** (что spec требует от PR-F.1):
- ✅ Папка `scripts/wiki/` создана
- ✅ `config.py` с тремя source-mode и списками источников
- ✅ `utils.py` с базовыми хелперами
- ✅ `compile.py` принимает `--source-mode`, диспатчит (логика — позже)
- ✅ README + упоминание в CLAUDE.md
- ✅ Тесты pytest
- ❌ Хуки `.claude/settings.json` — НЕ в этом PR (PR-F.4)
- ❌ Логика компиляции — НЕ в этом PR (PR-F.2/F.3/F.4)

**Что НЕ покрывает PR-F.1:**
- Не зовёт `claude-agent-sdk` (он добавится в PR-F.2 в requirements)
- Не пишет в `wiki/` папку (только stub-печать)
- Не трогает `template/`

Это правильно по YAGNI — каждый PR закрывает один уровень.

**Type consistency:**
- `config.SOURCE_MODES` (tuple), `config.SYSTEM_SOURCES` (list of dict), `config.WIKI_DIR` (Path) — используются единообразно в `compile.py` и тестах.
- `utils.slugify` → str, `utils.parse_frontmatter` → (dict, str) — типы согласованы с тестами.

**Placeholder scan:** нет TODO/TBD/«позже».

Plan complete.

---

## Дальше после PR-F.1

PR-F.2 — реализация `--source-mode=system`:
- Добавить `claude-agent-sdk` в requirements
- Реализовать обход `SYSTEM_SOURCES`, чтение MD/YAML, генерация концептов через SDK
- Первый bootstrap: запустить и получить `landing-system/wiki/`
- Коммит сгенерированной wiki в git
- План пишем когда подойдём.

PR-F.3 — `--source-mode=project-graph` + `template/`.
PR-F.4 — хуки + `--source-mode=conversations`.
PR-F.5 — `lint.py` + `preview.html`.
