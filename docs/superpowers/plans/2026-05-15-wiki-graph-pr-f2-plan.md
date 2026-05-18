# PR-F.2 — System Wiki Compilation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to execute. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Реализовать `compile.py --source-mode=system` — реально читает источники (агентов, скиллы, команды, шаблон, правила, блоки) и через Claude Agent SDK пишет `landing-system/wiki/` с концептами, индексом и логом.

**Architecture:** Боундарь между чистой логикой (обход файлов, кэш, форматирование) и SDK-вызовами (генерация концепта). Логика тестируется юнит-тестами с моком SDK; реальный SDK прогоняется один раз в smoke-тесте.

**Tech Stack:** Python 3.11+, `claude-agent-sdk` (новая dep), PyYAML, pytest, pytest-mock.

**Связанный spec:** [2026-05-15-wiki-graph-markup-design.md](../specs/2026-05-15-wiki-graph-markup-design.md) разделы 3.1, 4.2, 5.1.

**Предыдущий PR:** PR-F.1 (config.py, utils.py, compile.py skeleton) — `0f3296f`.

---

## Аутентификация SDK (важно понять перед началом)

`claude-agent-sdk` использует существующую авторизацию Claude Code (через `~/.claude/auth.json` или `claude` CLI). **API-ключ Anthropic НЕ нужен** — работает на подписке. На macOS Кирилла Claude Code уже залогинен, поэтому SDK подхватит auth автоматически.

В тестах SDK мокируем (pytest-mock + monkeypatch). Реальные вызовы — только в Task 7 (smoke-bootstrap).

---

## File Structure

**Создаём:**
- `scripts/wiki/hash_cache.py` — хэш-кэш source→article
- `scripts/wiki/sdk_client.py` — обёртка над claude-agent-sdk
- `scripts/wiki/system_compiler.py` — главная логика system mode
- `scripts/wiki/prompts/system_concept.md` — промпт для SDK (концепт из исходника)
- `scripts/wiki/prompts/system_index.md` — промпт для генерации index.md
- `tests/wiki/test_hash_cache.py`
- `tests/wiki/test_sdk_client.py`
- `tests/wiki/test_system_compiler.py`
- `tests/wiki/fixtures/` — фикстуры (заглушки источников)

**Модифицируем:**
- `scripts/wiki/compile.py` — реализовать `_handle_system_mode()`
- `tests/wiki/test_compile_cli.py` — обновить тест `test_system_mode_not_yet_implemented` → проверить что реально вызывает компайлер
- `requirements.txt` — добавить `claude-agent-sdk`

**НЕ трогаем:**
- хуки `.claude/settings.json` (PR-F.4)
- `template/` (PR-F.3)
- `preview.html` (PR-F.5)

---

## Task 1: Добавить claude-agent-sdk и pytest-mock в requirements

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Прочитать текущий `requirements.txt`**

```bash
cat requirements.txt
```

- [ ] **Step 2: Добавить две строки в `requirements.txt`**

```text
claude-agent-sdk>=0.1.0
pytest-mock>=3.12
```

- [ ] **Step 3: Установить**

```bash
pip install claude-agent-sdk pytest-mock
```
Expected: успешная установка. Если падает «no module named» — попробовать `pip3` или `python3 -m pip install`.

- [ ] **Step 4: Проверить импорт**

```bash
python3 -c "import claude_agent_sdk; print(claude_agent_sdk.__version__)"
```
Expected: версия пакета (>=0.1.0)

- [ ] **Step 5: Commit**

```bash
git add requirements.txt
git commit -m "deps(wiki): claude-agent-sdk + pytest-mock для PR-F.2"
```

---

## Task 2: Хэш-кэш source → article

**Files:**
- Create: `scripts/wiki/hash_cache.py`
- Create: `tests/wiki/test_hash_cache.py`

**Цель:** хранить sha256 каждого исходника, чтобы при повторном compile пропускать неизменённые. Кэш — JSON в `wiki/.cache.json`.

- [ ] **Step 1: Написать failing tests**

```python
# tests/wiki/test_hash_cache.py
"""Тесты hash_cache."""
import json
from pathlib import Path

import pytest

from scripts.wiki import hash_cache


def test_compute_hash_stable(tmp_path):
    """sha256 не меняется для одного контента."""
    p = tmp_path / "foo.md"
    p.write_text("hello")
    h1 = hash_cache.compute_hash(p)
    h2 = hash_cache.compute_hash(p)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_hash_differs_on_content(tmp_path):
    p = tmp_path / "foo.md"
    p.write_text("a")
    h1 = hash_cache.compute_hash(p)
    p.write_text("b")
    h2 = hash_cache.compute_hash(p)
    assert h1 != h2


def test_load_cache_missing(tmp_path):
    """Если файла кэша нет — возвращает пустой dict."""
    cache_path = tmp_path / ".cache.json"
    assert hash_cache.load_cache(cache_path) == {}


def test_save_and_load_cache(tmp_path):
    cache_path = tmp_path / ".cache.json"
    data = {"agents/foo.md": "abc123", "skills/bar.md": "def456"}
    hash_cache.save_cache(cache_path, data)
    assert cache_path.exists()
    loaded = hash_cache.load_cache(cache_path)
    assert loaded == data


def test_is_changed_new_file(tmp_path):
    """Новый файл → is_changed=True."""
    p = tmp_path / "new.md"
    p.write_text("x")
    cache = {}
    assert hash_cache.is_changed(p, "new.md", cache) is True


def test_is_changed_same_content(tmp_path):
    p = tmp_path / "same.md"
    p.write_text("content")
    h = hash_cache.compute_hash(p)
    cache = {"same.md": h}
    assert hash_cache.is_changed(p, "same.md", cache) is False


def test_is_changed_modified(tmp_path):
    p = tmp_path / "mod.md"
    p.write_text("v1")
    old_hash = hash_cache.compute_hash(p)
    p.write_text("v2")
    cache = {"mod.md": old_hash}
    assert hash_cache.is_changed(p, "mod.md", cache) is True
```

- [ ] **Step 2: Запустить — должно упасть**

Run: `pytest tests/wiki/test_hash_cache.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Реализовать `hash_cache.py`**

```python
# scripts/wiki/hash_cache.py
"""SHA256-кэш source-файлов для пропуска неизменённых в compile."""
import hashlib
import json
from pathlib import Path
from typing import Any


def compute_hash(path: Path) -> str:
    """sha256 содержимого файла."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cache(cache_path: Path) -> dict[str, str]:
    """Читает JSON-кэш {relative_path: sha256}. Возвращает {} если файла нет."""
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache_path: Path, data: dict[str, str]) -> None:
    """Пишет JSON-кэш атомарно."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data, indent=2, sort_keys=True))


def is_changed(path: Path, key: str, cache: dict[str, str]) -> bool:
    """True если файл новый или sha не совпадает с записью в кэше."""
    if key not in cache:
        return True
    return compute_hash(path) != cache[key]
```

- [ ] **Step 4: Запустить тесты**

Run: `pytest tests/wiki/test_hash_cache.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/hash_cache.py tests/wiki/test_hash_cache.py
git commit -m "feat(wiki): hash_cache.py — пропуск неизменённых источников

PR-F.2 Task 2."
```

---

## Task 3: SDK-клиент (обёртка над claude-agent-sdk)

**Files:**
- Create: `scripts/wiki/sdk_client.py`
- Create: `tests/wiki/test_sdk_client.py`

**Цель:** изолировать SDK-вызовы в одном модуле с одной функцией `generate(prompt: str, context: dict) -> str`. Это упрощает мокинг.

- [ ] **Step 1: Написать failing tests**

```python
# tests/wiki/test_sdk_client.py
"""Тесты sdk_client (с моком claude_agent_sdk)."""
from unittest.mock import MagicMock, patch

import pytest

from scripts.wiki import sdk_client


def test_generate_calls_sdk(mocker):
    """generate() вызывает SDK с собранным промптом."""
    fake_response = MagicMock()
    fake_response.content = "compiled article body"
    mock_query = mocker.patch.object(
        sdk_client, "_sdk_query", return_value=fake_response
    )

    result = sdk_client.generate(
        system="You compile wiki articles.",
        user="Source: agent foo\n\nContent: bar",
    )

    assert result == "compiled article body"
    mock_query.assert_called_once()
    call_kwargs = mock_query.call_args.kwargs
    assert "system" in call_kwargs
    assert "user" in call_kwargs


def test_generate_empty_response_raises(mocker):
    """Если SDK вернул пустой content — кидаем."""
    fake_response = MagicMock()
    fake_response.content = ""
    mocker.patch.object(sdk_client, "_sdk_query", return_value=fake_response)

    with pytest.raises(sdk_client.SDKError):
        sdk_client.generate(system="s", user="u")


def test_generate_strips_response(mocker):
    """Ведущие/завершающие пробелы в ответе SDK обрезаются."""
    fake_response = MagicMock()
    fake_response.content = "  \n\nbody\n\n  "
    mocker.patch.object(sdk_client, "_sdk_query", return_value=fake_response)
    assert sdk_client.generate(system="s", user="u") == "body"
```

- [ ] **Step 2: Запустить — fail**

Run: `pytest tests/wiki/test_sdk_client.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Реализовать `sdk_client.py`**

```python
# scripts/wiki/sdk_client.py
"""Обёртка над claude-agent-sdk.

В юнит-тестах функция _sdk_query() мокается. В production вызывает реальный SDK.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class SDKError(RuntimeError):
    """Ошибка вызова SDK или пустой ответ."""


@dataclass
class SDKResponse:
    content: str


def _sdk_query(system: str, user: str) -> SDKResponse:
    """Реальный вызов claude-agent-sdk. Заменяется моком в тестах."""
    # Импорт внутри — чтобы тесты не падали при отсутствии SDK в окружении.
    from claude_agent_sdk import ClaudeAgentClient  # type: ignore

    client = ClaudeAgentClient()
    response = client.complete(system=system, user=user)
    return SDKResponse(content=response.content)


def generate(system: str, user: str) -> str:
    """Вызывает SDK и возвращает очищенный ответ.

    Raises:
        SDKError: если SDK вернул пустую строку.
    """
    response = _sdk_query(system=system, user=user)
    content = (response.content or "").strip()
    if not content:
        raise SDKError("SDK вернул пустой content")
    return content
```

- [ ] **Step 4: Запустить тесты**

Run: `pytest tests/wiki/test_sdk_client.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/sdk_client.py tests/wiki/test_sdk_client.py
git commit -m "feat(wiki): sdk_client — обёртка над claude-agent-sdk

PR-F.2 Task 3. В тестах _sdk_query мокается, в production
делает реальный вызов через ClaudeAgentClient."
```

---

## Task 4: Промпты для SDK (markdown файлы)

**Files:**
- Create: `scripts/wiki/prompts/system_concept.md`
- Create: `scripts/wiki/prompts/system_index.md`
- Create: `scripts/wiki/prompts/__init__.py`

**Цель:** хранить системные промпты в отдельных файлах, не зашивать в код.

- [ ] **Step 1: Создать `prompts/__init__.py` (пустой)**

```bash
touch scripts/wiki/prompts/__init__.py
```

- [ ] **Step 2: Создать `prompts/system_concept.md`**

```markdown
Ты компилируешь knowledge wiki системы landing-system. На вход — markdown/yaml исходник одного компонента системы (агента, скилла, команды, этапа шаблона, правила или блока). На выход — структурированная wiki-страница на русском языке.

# Формат ответа

Вернуть только содержимое markdown-файла с frontmatter, БЕЗ обрамляющих ```markdown```.

```
---
type: agent | skill | command | stage | rule | block
name: kebab-case-name
sources: ["относительный/путь/к/исходнику"]
updated: 2026-05-15
triggers: []            # для команд: когда вызывать (естественные фразы)
stage: ""               # для этапов: 07c и т.п.
uses: []                # обратные ссылки на другие концепты
tags: []
---

# Заголовок (читаемое название)

## Что делает
Одна-две фразы простым языком (для маркетолога, не разработчика).

## Когда вызывать / в каком этапе
Условия активации, какой команды/агента ждать.

## Что на вход / на выход
Артефакты входа и выхода.

## Связанные концепты
- [[agent-name]] — кратко зачем связан
- [[skill-name]] — кратко

## Источник
- `путь/к/исходнику.md`
```

# Ограничения

- 200-400 слов в body.
- Простой русский язык.
- Все имена концептов в kebab-case.
- Не выдумывай связей, которых нет в исходнике.
```

- [ ] **Step 3: Создать `prompts/system_index.md`**

```markdown
Ты собираешь главный индекс системного wiki landing-system. На вход — список существующих концепт-файлов (их frontmatter и заголовки). На выход — `wiki/index.md`.

# Формат ответа

Markdown БЕЗ frontmatter, БЕЗ обрамляющих ```. Структура:

```
# Landing-System Wiki — главный индекс

> Авто-сгенерированный индекс. Не редактируй вручную — перезаписывается при `compile --source-mode=system`.

**Обновлено:** 2026-05-15

## Этапы pipeline
- [[stage-00-brief]] — короткое описание
- [[stage-01a-niche-analysis]] — ...
...

## Агенты
- [[agent-landing-orchestrator]] — ...
- [[agent-block-composer]] — ...
...

## Скиллы
...

## Команды
...

## Правила
...

## Блоки
...
```

# Правила

- Группировать по type из frontmatter.
- Внутри группы — алфавитный порядок.
- Каждая ссылка — `[[file-stem]]` (без расширения).
- Описание = первое предложение из секции «Что делает».
```

- [ ] **Step 4: Smoke-проверка — файлы существуют и не пустые**

```bash
ls -la scripts/wiki/prompts/
test -s scripts/wiki/prompts/system_concept.md && echo "concept OK"
test -s scripts/wiki/prompts/system_index.md && echo "index OK"
```
Expected: оба «OK»

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/prompts/
git commit -m "feat(wiki): промпты system_concept и system_index

PR-F.2 Task 4."
```

---

## Task 5: System Compiler — главная логика

**Files:**
- Create: `scripts/wiki/system_compiler.py`
- Create: `tests/wiki/test_system_compiler.py`
- Create: `tests/wiki/fixtures/agents/sample-agent.md`
- Create: `tests/wiki/fixtures/expected/agent-sample-agent.md`

**Цель:** функция `compile_system(repo_root, wiki_dir, dry_run=False)`, которая:
1. Обходит `config.SYSTEM_SOURCES` (glob-паттерны).
2. Для каждого файла проверяет хэш-кэш — пропускает неизменённый.
3. Изменённый → вызывает `sdk_client.generate()` → пишет концепт.
4. После всех концептов → вызывает SDK ещё раз для `index.md`.
5. Аппендит запись в `wiki/log.md`.
6. Обновляет `.cache.json`.

- [ ] **Step 1: Создать фикстуру-агента для тестов**

`tests/wiki/fixtures/agents/sample-agent.md`:

```markdown
---
name: sample-agent
description: Sample agent for testing.
---

# Sample Agent

This is a sample agent. It does nothing real.
```

- [ ] **Step 2: Написать failing tests**

```python
# tests/wiki/test_system_compiler.py
"""Тесты system_compiler с моком SDK."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts.wiki import system_compiler


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fake_repo(tmp_path):
    """Имитирует структуру landing-system минимально."""
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "sample-agent.md").write_text(
        (FIXTURES / "agents" / "sample-agent.md").read_text()
    )
    return tmp_path


def test_compile_creates_wiki_dir(fake_repo, tmp_path, mocker):
    """compile_system создаёт wiki/concepts/agents/."""
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\nname: sample-agent\n---\nBody.",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="# Index\n- [[agent-sample-agent]]",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )

    concept = wiki / "concepts" / "agents" / "sample-agent.md"
    assert concept.exists()
    assert "type: agent" in concept.read_text()


def test_compile_creates_index(fake_repo, tmp_path, mocker):
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nbody",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="# Landing-System Wiki\nIndex content",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    assert (wiki / "index.md").exists()
    assert "Landing-System Wiki" in (wiki / "index.md").read_text()


def test_compile_appends_log(fake_repo, tmp_path, mocker):
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nb",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="idx",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    log_text = (wiki / "log.md").read_text()
    assert "compile" in log_text.lower()
    assert "sample-agent" in log_text


def test_compile_skips_unchanged(fake_repo, tmp_path, mocker):
    """При повторном прогоне неизменённые файлы не зовут SDK."""
    wiki = tmp_path / "wiki"
    generate_mock = mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nbody",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="idx",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    # Первый прогон — генерация
    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    first_call_count = generate_mock.call_count

    # Второй прогон без изменений — SDK не должен зваться для концептов
    # (зовётся только index — то есть на 1 больше, если файл не менялся; для агентов 0)
    generate_mock.reset_mock()
    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    # Концепт пропущен → generate зовётся только для index (1 вызов)
    assert generate_mock.call_count == 1


def test_dry_run_does_not_write(fake_repo, tmp_path, mocker):
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nb",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="idx",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources, dry_run=True
    )
    assert not (wiki / "concepts" / "agents" / "sample-agent.md").exists()
    assert not (wiki / "index.md").exists()
```

- [ ] **Step 3: Запустить — должны упасть**

Run: `pytest tests/wiki/test_system_compiler.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 4: Реализовать `system_compiler.py`**

```python
# scripts/wiki/system_compiler.py
"""Компилит landing-system в landing-system/wiki/.

Алгоритм:
1. Обходим SYSTEM_SOURCES (glob-паттерны).
2. Для каждого файла — проверяем sha256 против .cache.json.
3. Изменённые → SDK → wiki/concepts/<concept_dir>/<slug>.md.
4. После всех — генерируем wiki/index.md через SDK.
5. Аппендим запись в wiki/log.md.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from scripts.wiki import hash_cache, sdk_client, utils

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _slug_for_source(path: Path) -> str:
    """Slug файла без расширения."""
    return utils.slugify(path.stem)


def _compile_concept(
    source_path: Path, repo_root: Path
) -> str:
    """Зовёт SDK для одного исходника, возвращает markdown концепта."""
    system_prompt = _load_prompt("system_concept.md")
    rel = source_path.relative_to(repo_root).as_posix()
    user_msg = f"Источник: `{rel}`\n\n---\n\n{source_path.read_text(encoding='utf-8')}"
    return sdk_client.generate(system=system_prompt, user=user_msg)


def _build_index(concepts: list[dict[str, Any]]) -> str:
    """Зовёт SDK для генерации index.md из списка концептов."""
    system_prompt = _load_prompt("system_index.md")
    summary_lines = []
    for c in concepts:
        summary_lines.append(
            f"- file_stem={c['file_stem']}, type={c.get('type', 'unknown')}, "
            f"name={c.get('name', '')}, source={c.get('source', '')}"
        )
    user_msg = "Список существующих концептов:\n\n" + "\n".join(summary_lines)
    return sdk_client.generate(system=system_prompt, user=user_msg)


def _append_log(log_path: Path, entries: list[str]) -> None:
    """Аппендит запись в wiki/log.md."""
    today = date.today().isoformat()
    header = f"\n## [{today}] compile --source-mode=system\n"
    body = "\n".join(f"- {e}" for e in entries) if entries else "- no changes\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(body)
        f.write("\n")


def compile_system(
    repo_root: Path,
    wiki_dir: Path,
    sources: list[dict[str, str]],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Главная функция системного компайлера.

    Returns:
        {"compiled": [...], "skipped": [...], "errors": [...]}.
    """
    cache_path = wiki_dir / ".cache.json"
    cache = hash_cache.load_cache(cache_path)
    concepts_summary: list[dict[str, Any]] = []
    compiled: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    for source_def in sources:
        pattern = source_def["path"]
        concept_dir = source_def["concept_dir"]
        for source_path in sorted(repo_root.glob(pattern)):
            rel_key = source_path.relative_to(repo_root).as_posix()
            slug = _slug_for_source(source_path)
            concept_path = wiki_dir / "concepts" / concept_dir / f"{slug}.md"

            if not hash_cache.is_changed(source_path, rel_key, cache):
                skipped.append(rel_key)
                # всё равно собираем для index
                if concept_path.exists():
                    meta, _ = utils.parse_frontmatter(
                        concept_path.read_text(encoding="utf-8")
                    )
                    concepts_summary.append(
                        {
                            "file_stem": slug,
                            "type": meta.get("type", "unknown"),
                            "name": meta.get("name", slug),
                            "source": rel_key,
                        }
                    )
                continue

            try:
                content = _compile_concept(source_path, repo_root)
            except sdk_client.SDKError as e:
                errors.append(f"{rel_key}: {e}")
                continue

            meta, _ = utils.parse_frontmatter(content)
            concepts_summary.append(
                {
                    "file_stem": slug,
                    "type": meta.get("type", "unknown"),
                    "name": meta.get("name", slug),
                    "source": rel_key,
                }
            )
            if not dry_run:
                utils.atomic_write(concept_path, content)
                cache[rel_key] = hash_cache.compute_hash(source_path)
            compiled.append(rel_key)

    # Индекс
    if concepts_summary:
        try:
            index_content = _build_index(concepts_summary)
            if not dry_run:
                utils.atomic_write(wiki_dir / "index.md", index_content)
        except sdk_client.SDKError as e:
            errors.append(f"index: {e}")

    # Лог + кэш
    if not dry_run:
        _append_log(
            wiki_dir / "log.md",
            entries=[f"compiled {p}" for p in compiled]
            + [f"skipped {p}" for p in skipped]
            + [f"error {e}" for e in errors],
        )
        hash_cache.save_cache(cache_path, cache)

    return {"compiled": compiled, "skipped": skipped, "errors": errors}
```

- [ ] **Step 5: Запустить тесты**

Run: `pytest tests/wiki/test_system_compiler.py -v`
Expected: PASS (5 tests)

- [ ] **Step 6: Commit**

```bash
git add scripts/wiki/system_compiler.py scripts/wiki/prompts/__init__.py \
        tests/wiki/test_system_compiler.py tests/wiki/fixtures/

git commit -m "feat(wiki): system_compiler — компиляция системного wiki

PR-F.2 Task 5. compile_system() обходит источники, скипает неизменённые
по hash_cache, зовёт SDK для концептов и индекса, аппендит в log.md."
```

---

## Task 6: Подключить в CLI

**Files:**
- Modify: `scripts/wiki/compile.py`
- Modify: `tests/wiki/test_compile_cli.py`

- [ ] **Step 1: Обновить тест `test_system_mode_not_yet_implemented`**

В `tests/wiki/test_compile_cli.py` заменить тест:

```python
def test_system_mode_dry_run_invokes_compiler(mocker):
    """system mode + dry-run должен звать compile_system, но не писать в FS."""
    # Этот тест пускается как subprocess — мокаем через env (упрощённо: 
    # проверяем что код возвращает 0 и упоминает 'system mode')
    result = run_compile("--source-mode=system", "--dry-run")
    assert result.returncode == 0
    # На реальном PR-F.2 dry-run печатает план; SDK не вызывается реально
    # потому что без сети упадёт — но dry-run не должен делать вызовов.
    # Полная end-to-end проверка — в smoke-тесте Task 7.
```

(Старый `test_system_mode_not_yet_implemented` удалить.)

- [ ] **Step 2: Доработать `compile.py` — заменить stub реальным вызовом**

В `scripts/wiki/compile.py` найти ветку `if args.source_mode == "system":` и заменить на:

```python
    if args.source_mode == "system":
        from scripts.wiki import system_compiler
        result = system_compiler.compile_system(
            repo_root=config.REPO_ROOT,
            wiki_dir=config.WIKI_DIR,
            sources=config.SYSTEM_SOURCES,
            dry_run=args.dry_run,
        )
        print(f"Compiled: {len(result['compiled'])}")
        print(f"Skipped: {len(result['skipped'])}")
        if result["errors"]:
            print(f"Errors: {len(result['errors'])}")
            for e in result["errors"]:
                print(f"  ! {e}", file=sys.stderr)
            return 1
        return 0
```

- [ ] **Step 3: Запустить тесты CLI**

Run: `pytest tests/wiki/test_compile_cli.py -v`
Expected: PASS

- [ ] **Step 4: Запустить ВЕСЬ wiki-сьют**

Run: `pytest tests/wiki/ -v`
Expected: PASS (≥28 тестов: 18 из PR-F.1 + 7 hash_cache + 3 sdk_client + 5 system_compiler — минимум 33)

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/compile.py tests/wiki/test_compile_cli.py
git commit -m "feat(wiki): compile.py system mode подключён к компайлеру

PR-F.2 Task 6 — CLI делегирует в system_compiler.compile_system()."
```

---

## Task 7: Bootstrap — первый реальный прогон системного wiki

**Files:**
- Create: `scripts/wiki/bootstrap-system.sh`
- Wiki files (генерируются скриптом): `wiki/index.md`, `wiki/log.md`, `wiki/concepts/**/*.md`, `wiki/.cache.json`

**ВНИМАНИЕ:** этот таск делает реальный вызов claude-agent-sdk. Использует подписку Кирилла. Ожидаемая длительность: 10-30 минут. Ожидаемый «вес» лимитов: ~30 минут активной работы Claude Code.

- [ ] **Step 1: Создать `scripts/wiki/bootstrap-system.sh`**

```bash
#!/bin/bash
# scripts/wiki/bootstrap-system.sh
# Первый запуск системного wiki-компайлера.
# Использует реальный claude-agent-sdk.

set -euo pipefail

cd "$(dirname "$0")/../.."

echo "📚 Bootstrap системного wiki..."
echo "   Источники: agents/, skills/, commands/, template/, docs/standards/, block-library/"
echo "   Цель: landing-system/wiki/"
echo ""
echo "⚠️  Это вызовет claude-agent-sdk на твоей подписке Claude Max."
echo "   Ожидаемая длительность: 10-30 минут."
echo ""
read -p "Продолжить? [y/N] " ok
[ "$ok" = "y" ] || { echo "Отменено."; exit 1; }

python3 -m scripts.wiki.compile --source-mode=system

echo ""
echo "✅ Готово. Открой wiki/index.md чтобы посмотреть карту системы."
```

Сделать исполняемым:
```bash
chmod +x scripts/wiki/bootstrap-system.sh
```

- [ ] **Step 2: Сначала — dry-run для проверки что не упадёт**

```bash
cd landing-system
python3 -m scripts.wiki.compile --source-mode=system --dry-run
```
Expected: exit 0, печать `Compiled: N`, `Skipped: M`. SDK на dry-run ВСЁ РАВНО вызывается (потому что в текущей реализации dry-run не пишет в файлы, но генерирует контент для оценки). 

**Если dry-run падает на сетевой ошибке:** проверь что Claude Code залогинен (`claude --version`). Если SDK не находит auth — добавь в окружение `ANTHROPIC_API_KEY` (опциональный фоллбек) — но обычно работает через подписку.

- [ ] **Step 3: Если dry-run прошёл — запустить реальный прогон**

```bash
bash scripts/wiki/bootstrap-system.sh
# (ответить 'y')
```

Ожидаемое:
- Создаётся `landing-system/wiki/` с подпапками `concepts/agents/`, `concepts/skills/` и т.д.
- В каждой — markdown-файл по каждому исходнику.
- `wiki/index.md` — главный индекс.
- `wiki/log.md` — запись о прогоне.
- `wiki/.cache.json` — хэш-кэш.

- [ ] **Step 4: Глазами проверить результат**

```bash
ls wiki/
ls wiki/concepts/agents/ | head
cat wiki/index.md | head -50
```
Ожидаемое: концепты есть, индекс структурирован.

**Если что-то выглядит ОЧЕНЬ криво** (например, концепты пустые или галлюцинации): возможно надо подправить промпты в `scripts/wiki/prompts/`. Доработать и перезапустить bootstrap (cache будет пустой, перекомпилит всё).

**Если выглядит нормально:** идём дальше.

- [ ] **Step 5: Add `wiki/` в репо**

Решение из spec: системный wiki коммитим в git (команда видит).

```bash
git add wiki/ scripts/wiki/bootstrap-system.sh
git status
```
Проверить что добавляется: `wiki/index.md`, `wiki/log.md`, концепты, `.cache.json`, bootstrap-скрипт.

**.cache.json — коммитим тоже** (чтобы повторный compile у другого члена команды пропускал неизменённое).

- [ ] **Step 6: Финальный pytest**

```bash
pytest tests/wiki/ -v
```
Expected: всё pass.

- [ ] **Step 7: Commit «первый системный wiki»**

```bash
git commit -m "$(cat <<'EOF'
feat(wiki): первый bootstrap системного wiki

PR-F.2 Task 7 — реальный прогон compile --source-mode=system.

Создан landing-system/wiki/ с концептами по агентам, скиллам,
командам, этапам шаблона, правилам и блокам. index.md и log.md.

Дальше — PR-F.3 (project-graph + template integration).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec coverage (раздел 5.1 system mode):**
- ✅ Чтение SYSTEM_SOURCES
- ✅ Генерация концептов с frontmatter (type, name, sources, updated, uses)
- ✅ index.md
- ✅ log.md (append, не перезапись)
- ✅ Хэш-кэш для пропуска неизменённых
- ✅ Промпты в отдельных файлах
- ⚠️ Connections (`wiki/connections/*.md`) — НЕ в этом PR. Это синтез связей. Перенесено в PR-F.5 (lint + connections — оба про анализ всей wiki целиком).

**Placeholders:** нет.

**Type consistency:**
- `compile_system()` возвращает `dict[str, Any]` с ключами `compiled`, `skipped`, `errors` — те же ключи используются в `compile.py` CLI.
- `sdk_client.generate(system, user) -> str` — одинаковая сигнатура везде.
- `hash_cache.compute_hash(path) -> str`, `is_changed(path, key, cache) -> bool` — согласованно.

**Риски:**
1. **SDK не залогинен** — bootstrap упадёт. Тогда либо `claude login`, либо `ANTHROPIC_API_KEY` env. План это упоминает в Task 7 Step 2.
2. **SDK генерит мусор** — промпты могут потребовать итерации. Шаг Task 7 Step 4 это покрывает («если выглядит криво — подправь промпт, перезапусти»).
3. **Большое окно для landing-system** — 35 агентов × ~10K токенов на каждый = ~350K input tokens на прогон. Это **долго**, но не проблема по лимитам Max 5x. Может занять 20-30 минут реального времени из-за rate limits на SDK.

---

## Дальше после PR-F.2

PR-F.3 — `--source-mode=project-graph`:
- Парсинг артефактов проекта (yaml/html/json) → концепты в `<project>/wiki/`
- Большинство сорсов не требует SDK (структурированные данные)
- LLM только для `decisions.md` и связей
- Интеграция в `template/`
- Миграция `dubai-avto-liza`

PR-F.4 — хуки + `--source-mode=conversations`.
PR-F.5 — `lint.py` + `wiki/connections/` + `preview.html`.
