# PR-F.4 — Hooks + Conversation Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Подключить три хука Claude Code (`SessionStart`, `SessionEnd`, `PreCompact`) для двух режимов:
- В `landing-system/.claude/settings.json` — для сессий разработки системы.
- В `template/.claude/settings.json` (наследуется новыми проектами) — для сессий по конкретному лендингу.

Также реализовать `--source-mode=conversations` — компиляция daily логов сессий в `memory/compiled/`. Это даёт **главный эффект из видео**: агент при старте знает всё, что было в прошлой сессии.

**Architecture:** Хуки — тонкие Python-скрипты, делегирующие в `scripts/wiki/`. SessionStart **синхронный** (быстро, до 1 сек). SessionEnd **запускает детач-процесс** (flush + compile в фоне). PreCompact — страховка от потери данных при авто-сжатии.

**Tech Stack:** Python, claude-agent-sdk (для flush), subprocess (для детача).

**Связанный spec:** разделы 4.3, 4.4, 5.1 (conversations mode).

**Предыдущий PR:** PR-F.3 (project-graph + template).

---

## File Structure

**Создаём:**
- `scripts/wiki/hooks/__init__.py`
- `scripts/wiki/hooks/session_start.py` — печатает индексы wiki/memory в stdout (Claude Code их инжектит в контекст)
- `scripts/wiki/hooks/session_end.py` — спавнит detached `flush.py`
- `scripts/wiki/hooks/pre_compact.py` — сохраняет частичный транскрипт
- `scripts/wiki/flush.py` — читает транскрипт, через SDK извлекает уроки → `daily/YYYY-MM-DD.md`
- `scripts/wiki/conversations_compiler.py` — `--source-mode=conversations`: компилит daily/ в memory/compiled/
- `scripts/wiki/prompts/flush.md` — промпт для извлечения уроков
- `scripts/wiki/prompts/conversations_concept.md` — промпт для compile концептов
- `tests/wiki/test_hooks.py` — тесты что хуки запускаются без ошибок
- `tests/wiki/test_flush.py` — тесты flush с моком SDK
- `tests/wiki/test_conversations_compiler.py`

**Модифицируем:**
- `.claude/settings.json` (landing-system) — добавить hooks
- `template/.claude/settings.json` — создать с hooks
- `scripts/wiki/compile.py` — реализовать ветку `conversations`

---

## Task 1: Hook scripts (тонкие обёртки)

**Файлы:**
- Create: `scripts/wiki/hooks/{__init__.py,session_start.py,session_end.py,pre_compact.py}`
- Create: `tests/wiki/test_hooks.py`

**Принцип хуков Claude Code:** хук получает JSON через stdin с метаданными (cwd, transcript path, session_id и т.д.), пишет в stdout то что вставится в контекст агента (SessionStart) или просто завершается (SessionEnd / PreCompact).

- [ ] **Step 1: Прочитать формат claude-code hooks**

Run: `cat ~/.claude/settings.json | head` — посмотреть структуру hooks (если есть) или
```bash
python3 -c "
# Документация формата hooks из Claude Code:
# Хук получает stdin JSON: {cwd, transcript_path, session_id, source}
# SessionStart: stdout → инжектится в системный контекст агента
# SessionEnd: stdout не используется (агент уже ушёл)
# PreCompact: stdout не инжектится, но скрипт может писать в FS
"
```

- [ ] **Step 2: Создать пустой `__init__.py`**

```bash
touch scripts/wiki/hooks/__init__.py
```

- [ ] **Step 3: Создать `session_start.py`**

```python
#!/usr/bin/env python3
"""SessionStart hook: печатает wiki/index + memory index в stdout.

Claude Code инжектит вывод как system context.

Логика:
1. cwd = текущая папка сессии (передаётся через stdin JSON).
2. Если cwd внутри landing-system/ → читать landing-system/wiki/index.md.
3. Если cwd похож на ~/Lendings/<slug>/ → читать <slug>/wiki/index.md + последний daily log.
4. Если оба пути актуальны (например работаем в landing-system над проектом)
   → инжектить ОБА индекса.

Скрипт быстрый (<1 сек), без сетевых вызовов.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


LANDING_SYSTEM = Path(__file__).resolve().parents[2]


def _read_or_empty(p: Path, max_chars: int = 8000) -> str:
    if not p.exists():
        return ""
    try:
        text = p.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[...обрезано]"
        return text
    except OSError:
        return ""


def _detect_project_slug(cwd: Path) -> str | None:
    """Если cwd внутри ~/Lendings/<slug>/ — вернуть slug."""
    lendings = Path.home() / "Lendings"
    try:
        rel = cwd.resolve().relative_to(lendings)
    except ValueError:
        return None
    parts = rel.parts
    return parts[0] if parts else None


def _latest_daily(memory_dir: Path) -> str:
    """Читает последний файл из memory/daily/."""
    daily = memory_dir / "daily"
    if not daily.exists():
        return ""
    files = sorted(daily.glob("*.md"))
    if not files:
        return ""
    return _read_or_empty(files[-1], max_chars=4000)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    cwd_str = payload.get("cwd") or str(Path.cwd())
    cwd = Path(cwd_str)

    chunks: list[str] = []

    # Системный wiki — если работаем в landing-system или его дочерней папке
    try:
        cwd.resolve().relative_to(LANDING_SYSTEM)
        sys_index = LANDING_SYSTEM / "wiki" / "index.md"
        text = _read_or_empty(sys_index)
        if text:
            chunks.append(f"<system_wiki_index>\n{text}\n</system_wiki_index>")
    except ValueError:
        pass

    # Проектный wiki — если работаем в ~/Lendings/<slug>/
    slug = _detect_project_slug(cwd)
    if slug:
        project = Path.home() / "Lendings" / slug
        proj_index = _read_or_empty(project / "wiki" / "index.md")
        if proj_index:
            chunks.append(f"<project_wiki_index project=\"{slug}\">\n{proj_index}\n</project_wiki_index>")
        memory_recent = _latest_daily(project / "memory")
        if memory_recent:
            chunks.append(f"<project_recent_memory project=\"{slug}\">\n{memory_recent}\n</project_recent_memory>")

    if chunks:
        print("\n\n".join(chunks))

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Создать `session_end.py`**

```python
#!/usr/bin/env python3
"""SessionEnd hook: спавнит detached flush.py в фоне.

Не блокирует завершение сессии. flush сам разберётся с транскриптом.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
FLUSH = HERE.parent / "flush.py"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    transcript = payload.get("transcript_path", "")
    cwd = payload.get("cwd", str(Path.cwd()))

    if not transcript or not Path(transcript).exists():
        return 0

    # Detach: спавним процесс, не ждём завершения
    subprocess.Popen(
        ["python3", str(FLUSH), "--transcript", transcript, "--cwd", cwd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Создать `pre_compact.py`**

```python
#!/usr/bin/env python3
"""PreCompact hook: страховка перед авто-сжатием контекста.

Логика та же что у session_end — спавним flush detached.
Это сохраняет уроки из текущей сессии ДО того как Claude её сожмёт.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
FLUSH = HERE.parent / "flush.py"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    transcript = payload.get("transcript_path", "")
    cwd = payload.get("cwd", str(Path.cwd()))

    if not transcript or not Path(transcript).exists():
        return 0

    subprocess.Popen(
        ["python3", str(FLUSH), "--transcript", transcript, "--cwd", cwd, "--mode", "pre-compact"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Тест что хуки запускаются без ошибки**

```python
# tests/wiki/test_hooks.py
"""Smoke-тесты хуков — что они принимают пустой stdin и не падают."""
import json
import subprocess
import sys
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[2] / "scripts" / "wiki" / "hooks"


def test_session_start_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input="{}",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_session_start_invalid_json():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0  # не падает на мусоре


def test_session_end_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_end.py")],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0


def test_pre_compact_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "pre_compact.py")],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0


def test_session_start_injects_landing_system_index(tmp_path, monkeypatch):
    """Когда cwd = landing-system/, в выводе должен быть system_wiki_index."""
    # Имитация: указываем cwd как landing-system
    repo = Path(__file__).resolve().parents[2]
    payload = {"cwd": str(repo)}
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Если wiki/index.md есть — должен быть упомянут
    if (repo / "wiki" / "index.md").exists():
        assert "system_wiki_index" in result.stdout
```

- [ ] **Step 7: Запустить тесты**

Run: `chmod +x scripts/wiki/hooks/*.py && pytest tests/wiki/test_hooks.py -v`
Expected: 5 PASS

- [ ] **Step 8: Commit**

```bash
git add scripts/wiki/hooks/ tests/wiki/test_hooks.py
git commit -m "feat(wiki): хуки SessionStart/End/PreCompact

PR-F.4 Task 1. session_start читает индексы и инжектит в контекст,
session_end и pre_compact спавнят detached flush.py."
```

---

## Task 2: `flush.py` — извлечение уроков через SDK

**Files:**
- Create: `scripts/wiki/flush.py`
- Create: `scripts/wiki/prompts/flush.md`
- Create: `tests/wiki/test_flush.py`
- Create: `tests/wiki/fixtures/transcripts/sample.jsonl`

- [ ] **Step 1: Создать `prompts/flush.md`**

```markdown
Ты извлекаешь полезные уроки из транскрипта сессии Claude Code. Транскрипт — JSON Lines (одно сообщение в строке).

# Что искать

- **Решения** — что пользователь решил по вопросу архитектуры/дизайна/контента.
- **Уроки** — что узнали в процессе (новый факт, ошибка, способ решения).
- **Грабли** — на чём споткнулись и как обошли.
- **TODO** — что отложили на следующую сессию.

# Что игнорировать

- Стандартные ответы агента типа «давай сделаем X».
- Команды cli, ls, grep — без выводов.
- Мелкие технические детали (точные имена файлов, размеры — если не критичны).

# Формат вывода

Markdown БЕЗ frontmatter, БЕЗ обрамляющих ```:

```
- **[решение]** Решили взять цены с конкурентов. Контекст: клиент не дал цен.
- **[урок]** verify-composed-premium.sh падает если фотки нет в processed/. Фикс: photo-curator должен класть и в processed/.
- **[грабли]** Bootstrap wiki падал из-за того что pythonpath не включал scripts/. Добавили pythonpath=. в pytest.ini.
- **[todo]** Доделать миграцию dubai-avto-liza под PR-F.3.
```

# Ограничения

- 5-15 пунктов максимум.
- Простой русский.
- Каждый пункт самостоятельный (не теряет смысл вне контекста).
- Если в транскрипте НИЧЕГО ценного — верни одну строку: `_(пусто)_`
```

- [ ] **Step 2: Создать `tests/wiki/fixtures/transcripts/sample.jsonl`**

```jsonl
{"role": "user", "content": "Помоги починить compile.py — падает"}
{"role": "assistant", "content": "Посмотрел код, проблема в импорте scripts.wiki. Нужно добавить pythonpath=. в pytest.ini"}
{"role": "user", "content": "Так и сделаем"}
{"role": "assistant", "content": "Готово, тесты прошли"}
```

- [ ] **Step 3: Написать failing tests**

```python
# tests/wiki/test_flush.py
"""Тесты flush.py с моком SDK."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.wiki import flush


FIXTURES = Path(__file__).parent / "fixtures" / "transcripts"


def test_read_transcript():
    """Читает JSONL и возвращает list[dict]."""
    msgs = flush.read_transcript(FIXTURES / "sample.jsonl")
    assert len(msgs) == 4
    assert msgs[0]["role"] == "user"


def test_format_transcript_for_sdk():
    """Превращает list[dict] в plain text для SDK."""
    msgs = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    text = flush.format_transcript(msgs)
    assert "user: hello" in text.lower()
    assert "assistant: hi" in text.lower()


def test_flush_writes_daily_log(tmp_path, mocker):
    """flush() извлекает уроки и аппендит в daily/YYYY-MM-DD.md."""
    mocker.patch(
        "scripts.wiki.flush.sdk_client.generate",
        return_value="- **[урок]** Тестовый урок",
    )
    memory_dir = tmp_path / "memory"
    flush.flush_transcript(
        transcript_path=FIXTURES / "sample.jsonl",
        memory_dir=memory_dir,
    )
    daily = memory_dir / "daily"
    assert daily.exists()
    files = list(daily.glob("*.md"))
    assert len(files) == 1
    assert "Тестовый урок" in files[0].read_text(encoding="utf-8")


def test_flush_skips_empty_result(tmp_path, mocker):
    """Если SDK вернул '_(пусто)_' — daily не создаётся."""
    mocker.patch(
        "scripts.wiki.flush.sdk_client.generate",
        return_value="_(пусто)_",
    )
    memory_dir = tmp_path / "memory"
    flush.flush_transcript(
        transcript_path=FIXTURES / "sample.jsonl",
        memory_dir=memory_dir,
    )
    daily = memory_dir / "daily"
    # Папка может быть создана, но без файлов
    if daily.exists():
        assert list(daily.glob("*.md")) == []
```

- [ ] **Step 4: Запустить — fail**

Run: `pytest tests/wiki/test_flush.py -v`

- [ ] **Step 5: Реализовать `flush.py`**

```python
# scripts/wiki/flush.py
"""Извлекает уроки из транскрипта Claude Code сессии через SDK.

Запускается detached из SessionEnd / PreCompact хуков.

Использование:
  python3 flush.py --transcript <path> --cwd <cwd> [--mode session-end|pre-compact]

Логика:
1. Читает transcript JSONL.
2. Определяет target memory/ по cwd (landing-system vs ~/Lendings/<slug>).
3. Зовёт SDK с промптом flush.md → markdown с уроками.
4. Аппендит в memory/daily/YYYY-MM-DD.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from scripts.wiki import sdk_client

PROMPTS_DIR = Path(__file__).parent / "prompts"
LANDING_SYSTEM = Path(__file__).resolve().parents[1]


def read_transcript(path: Path) -> list[dict]:
    """JSONL → list[dict]. Игнорирует битые строки."""
    msgs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msgs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return msgs


def format_transcript(msgs: list[dict]) -> str:
    """Plain text для SDK: 'role: content' с переносами."""
    lines = []
    for m in msgs:
        role = m.get("role", "?")
        content = m.get("content", "")
        if isinstance(content, list):
            # Claude Code Format: list of blocks
            content = " ".join(
                b.get("text", "") for b in content if isinstance(b, dict)
            )
        lines.append(f"{role}: {content}")
    return "\n\n".join(lines)


def _detect_memory_dir(cwd: Path) -> Path:
    """По cwd определяет куда писать memory/."""
    lendings = Path.home() / "Lendings"
    try:
        rel = cwd.resolve().relative_to(lendings)
        slug = rel.parts[0]
        return lendings / slug / "memory"
    except (ValueError, IndexError):
        pass
    # Fallback — landing-system/memory/
    return LANDING_SYSTEM / "memory"


def flush_transcript(transcript_path: Path, memory_dir: Path = None, cwd: Path = None) -> None:
    """Извлекает уроки и аппендит в daily log."""
    if memory_dir is None:
        memory_dir = _detect_memory_dir(cwd or Path.cwd())

    msgs = read_transcript(transcript_path)
    if not msgs:
        return

    text = format_transcript(msgs)
    # Ограничим вход (последние ~30 сообщений)
    if len(msgs) > 30:
        text = format_transcript(msgs[-30:])

    prompt = (PROMPTS_DIR / "flush.md").read_text(encoding="utf-8")
    try:
        lessons = sdk_client.generate(system=prompt, user=text)
    except sdk_client.SDKError:
        return  # silent — мы в фоне, не пугаем юзера

    if lessons.strip() in ("_(пусто)_", "_пусто_", ""):
        return

    daily = memory_dir / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    today_file = daily / f"{date.today().isoformat()}.md"

    header = f"\n## flush @ {date.today().isoformat()}\n\n"
    with today_file.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(lessons)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--cwd", default="")
    parser.add_argument("--mode", default="session-end")
    args = parser.parse_args()

    transcript = Path(args.transcript)
    if not transcript.exists():
        return 1
    cwd = Path(args.cwd) if args.cwd else Path.cwd()

    flush_transcript(transcript_path=transcript, cwd=cwd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Запустить тесты**

Run: `pytest tests/wiki/test_flush.py -v`
Expected: 4 PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/wiki/flush.py scripts/wiki/prompts/flush.md \
        tests/wiki/test_flush.py tests/wiki/fixtures/transcripts/
git commit -m "feat(wiki): flush.py — извлечение уроков из транскриптов

PR-F.4 Task 2."
```

---

## Task 3: `--source-mode=conversations` — компиляция daily в concepts

**Files:**
- Create: `scripts/wiki/conversations_compiler.py`
- Create: `scripts/wiki/prompts/conversations_concept.md`
- Create: `tests/wiki/test_conversations_compiler.py`
- Modify: `scripts/wiki/compile.py`

**Цель:** Превращает daily/YYYY-MM-DD.md (которые состоят из коротких bullet points) в концепт-статьи в `memory/compiled/concepts/`.

- [ ] **Step 1: Создать `prompts/conversations_concept.md`**

```markdown
Ты группируешь похожие уроки из daily logs сессий в концепт-статьи. На вход — все daily logs за период. На выход — несколько концептов на русском.

# Формат каждого концепта

```
---
type: conversation-concept
name: kebab-case-name
sources: ["daily/2026-05-15.md", "daily/2026-05-14.md"]
updated: 2026-05-15
tags: [tag1, tag2]
---

# Заголовок концепта

## Суть
Одна-две фразы.

## Контекст
Откуда это всплыло (какая работа велась).

## Принятое решение / урок
Конкретика — что делать или о чём помнить.
```

# Правила группировки

- Объединяй похожие пункты из разных дней в один концепт.
- Один концепт ≈ одна тема.
- Создавай столько концептов сколько нужно (от 1 до 10 на сессию compile).
- Не дублируй то что уже есть.

# Формат ответа

Несколько концептов, разделённых строкой `---END---`:

```
<frontmatter + body первого концепта>
---END---
<frontmatter + body второго концепта>
---END---
```

Без обрамляющих ``` ```.
```

- [ ] **Step 2: failing test `tests/wiki/test_conversations_compiler.py`**

```python
"""Тесты conversations_compiler."""
from pathlib import Path

import pytest

from scripts.wiki import conversations_compiler


@pytest.fixture
def fake_memory(tmp_path):
    daily = tmp_path / "daily"
    daily.mkdir()
    (daily / "2026-05-15.md").write_text(
        "- **[решение]** Цены берём у конкурентов\n"
        "- **[урок]** verify-composed падает без processed/"
    )
    (daily / "2026-05-14.md").write_text(
        "- **[грабли]** Bootstrap падал без pythonpath\n"
    )
    return tmp_path


def test_compile_creates_compiled_dir(fake_memory, mocker):
    mocker.patch(
        "scripts.wiki.conversations_compiler.sdk_client.generate",
        return_value=(
            "---\ntype: conversation-concept\nname: prices-from-competitors\n---\n"
            "# Цены\n\nРешили брать у конкурентов.\n"
        ),
    )
    conversations_compiler.compile_conversations(memory_root=fake_memory)
    assert (fake_memory / "compiled" / "concepts").exists()


def test_compile_writes_concept_files(fake_memory, mocker):
    sdk_output = (
        "---\ntype: conversation-concept\nname: prices\n---\n# Цены\n\nA\n"
        "---END---\n"
        "---\ntype: conversation-concept\nname: bootstrap-fix\n---\n# Bootstrap\n\nB\n"
    )
    mocker.patch(
        "scripts.wiki.conversations_compiler.sdk_client.generate",
        return_value=sdk_output,
    )
    conversations_compiler.compile_conversations(memory_root=fake_memory)
    concepts = list((fake_memory / "compiled" / "concepts").glob("*.md"))
    assert len(concepts) == 2
    names = {c.stem for c in concepts}
    assert "prices" in names
    assert "bootstrap-fix" in names


def test_compile_handles_empty_dailies(tmp_path, mocker):
    """Если daily/ пустая — ничего не пишем."""
    (tmp_path / "daily").mkdir()
    gen = mocker.patch(
        "scripts.wiki.conversations_compiler.sdk_client.generate",
        return_value="x",
    )
    conversations_compiler.compile_conversations(memory_root=tmp_path)
    gen.assert_not_called()
```

- [ ] **Step 3: Запустить — fail**

Run: `pytest tests/wiki/test_conversations_compiler.py -v`

- [ ] **Step 4: Реализовать `conversations_compiler.py`**

```python
# scripts/wiki/conversations_compiler.py
"""Компилит daily/ → memory/compiled/concepts/.

Зовётся хуком SessionEnd или вручную:
  python -m scripts.wiki.compile --source-mode=conversations --project=<slug>
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts.wiki import sdk_client, utils

PROMPTS_DIR = Path(__file__).parent / "prompts"


def compile_conversations(memory_root: Path) -> dict:
    """memory_root содержит daily/ и (генерируется) compiled/."""
    daily = memory_root / "daily"
    if not daily.exists():
        return {"written": []}

    files = sorted(daily.glob("*.md"))
    if not files:
        return {"written": []}

    # Объединяем содержимое всех daily
    combined = "\n\n".join(
        f"## {f.stem}\n\n{f.read_text(encoding='utf-8')}" for f in files
    )

    prompt = (PROMPTS_DIR / "conversations_concept.md").read_text(encoding="utf-8")
    try:
        sdk_out = sdk_client.generate(system=prompt, user=combined)
    except sdk_client.SDKError:
        return {"written": [], "errors": ["SDK failed"]}

    # Парсим вывод — концепты разделены ---END---
    concepts_dir = memory_root / "compiled" / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for chunk in sdk_out.split("---END---"):
        chunk = chunk.strip()
        if not chunk:
            continue
        meta, body = utils.parse_frontmatter(chunk)
        name = meta.get("name") or "concept"
        slug = utils.slugify(name)
        path = concepts_dir / f"{slug}.md"
        utils.atomic_write(path, chunk)
        written.append(str(path.name))

    # log
    log = memory_root / "compiled" / "log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{date.today().isoformat()}] conversations compile\n")
        for w in written:
            f.write(f"- {w}\n")

    return {"written": written}
```

- [ ] **Step 5: Добавить ветку в `compile.py`**

В `scripts/wiki/compile.py` заменить ветку conversations:

```python
    if args.source_mode == "conversations":
        from pathlib import Path
        from scripts.wiki import conversations_compiler
        memory_root = Path.home() / "Lendings" / args.project / "memory"
        if not memory_root.exists():
            print(f"ERROR: memory dir not found: {memory_root}", file=sys.stderr)
            return 2
        result = conversations_compiler.compile_conversations(memory_root=memory_root)
        print(f"Conversations compiled: {len(result.get('written', []))}")
        return 0
```

- [ ] **Step 6: Тесты**

Run: `pytest tests/wiki/test_conversations_compiler.py -v && pytest tests/wiki/ -v`
Expected: все PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/wiki/conversations_compiler.py scripts/wiki/prompts/conversations_concept.md \
        scripts/wiki/compile.py tests/wiki/test_conversations_compiler.py
git commit -m "feat(wiki): conversations_compiler — daily/→concepts/

PR-F.4 Task 3."
```

---

## Task 4: Прописать хуки в settings.json

**Files:**
- Modify: `.claude/settings.json` (landing-system)
- Create: `template/.claude/settings.json`

**Формат хуков Claude Code:** ключ `hooks` в `settings.json`, внутри — массивы событий.

- [ ] **Step 1: Дописать `landing-system/.claude/settings.json`**

Найти поле `"hooks": {}` и заменить на:

```json
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${LANDING_SYSTEM_DIR:-.}/scripts/wiki/hooks/session_start.py"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${LANDING_SYSTEM_DIR:-.}/scripts/wiki/hooks/session_end.py"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${LANDING_SYSTEM_DIR:-.}/scripts/wiki/hooks/pre_compact.py"
          }
        ]
      }
    ]
  }
```

**Примечание:** `${LANDING_SYSTEM_DIR:-.}` — переменная окружения с фоллбеком на `.`. Если работает кривовато — заменить на абсолютный путь.

- [ ] **Step 2: Создать `template/.claude/settings.json`**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${LANDING_SYSTEM_DIR}/scripts/wiki/hooks/session_start.py"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${LANDING_SYSTEM_DIR}/scripts/wiki/hooks/session_end.py"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${LANDING_SYSTEM_DIR}/scripts/wiki/hooks/pre_compact.py"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Проверить JSON валиден**

```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo "landing-system OK"
python3 -m json.tool template/.claude/settings.json > /dev/null && echo "template OK"
```

- [ ] **Step 4: Smoke — что хуки вызываются**

```bash
# Симулируем session start через stdin
echo '{"cwd": "'"$(pwd)"'"}' | python3 scripts/wiki/hooks/session_start.py
```
Expected: либо пусто (если wiki/index.md ещё не создан), либо содержимое индекса.

- [ ] **Step 5: Commit**

```bash
git add .claude/settings.json template/.claude/settings.json
git commit -m "feat(wiki): хуки в settings.json (landing-system + template)

PR-F.4 Task 4 — SessionStart/End/PreCompact подключены."
```

---

## Self-Review

**Spec coverage (раздел 4.3, 4.4, 5.1 conversations):**
- ✅ Три хука в двух местах
- ✅ flush.py для извлечения уроков
- ✅ conversations_compiler (--source-mode=conversations)
- ✅ SessionStart инжектит system + project индексы
- ⏭️ Реальный smoke хука в живой сессии — отложено (рестарт Claude Code требует выхода из текущей сессии). Документация в README.

**Placeholders:** нет.

**Type consistency:**
- `compile_conversations(memory_root) -> dict` — совместим с CLI.
- `flush_transcript(transcript_path, memory_dir=None, cwd=None)` — keyword args, опциональные.

**Риски:**
1. **Хук падает при старте сессии** — может сломать запуск Claude Code. Митигация: хуки имеют `except (json.JSONDecodeError, ValueError)` и всегда возвращают 0.
2. **detached flush.py долго работает** — может перекрыть несколько сессий. Это OK — параллельные flush безопасны.
3. **`${LANDING_SYSTEM_DIR}` не задана** — хук не найдёт скрипт. Митигация: задать в onboarding (отдельная задача).

---

## Дальше после PR-F.4

PR-F.5 — финал:
- `lint.py` (7 проверок здоровья wiki, ~$0.15-0.25 за прогон)
- `query.py` (запрос с CLI)
- `preview.html` рендерер (для глазной проверки)
- Документация в `docs/SETUP.md` про Obsidian опционально
- Финальная end-to-end проверка

После PR-F.5 — push всех изменений одним логическим push.
