# Token Budget Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Расширить `wiki/routing-report.md` полным token budget — все источники токенов за сессию (wiki, framework loads, bash stdout, session_start инжекты) с выделением утечек.

**Architecture:** Новый event type `context_inject` в `logs/wiki-usage.jsonl`. Три точки записи: `session_start.py` (инжекты при старте сессии), `flush.py` (framework loads + bash stdout из транскрипта постфактум). `stats.py` агрегирует все типы событий в расширенный отчёт с секцией "Token Budget по категориям".

**Tech Stack:** Python 3.10+, pytest, stdlib only (json, pathlib, fnmatch).

---

## File Map

| Файл | Действие | Что меняется |
|------|----------|--------------|
| `scripts/wiki/routing_log.py` | Modify | Добавить `log_context_inject()` |
| `scripts/wiki/transcript_parser.py` | Modify | Добавить `output` в `ToolCall`, матчить `toolResult` по `toolUseId` |
| `scripts/wiki/config.py` | Modify | Расширить `SOURCE_READ_PATTERNS` |
| `scripts/wiki/hooks/session_start.py` | Modify | Логировать project_wiki и project_memory инжекты |
| `scripts/wiki/flush.py` | Modify | Логировать framework_load и bash_stdout |
| `scripts/wiki/stats.py` | Modify | Расширить `StatsResult`, `compute_stats()`, `generate_report()`, `one_line_summary()` |
| `tests/wiki/test_routing_log_context_inject.py` | Create | Тесты для `log_context_inject()` |
| `tests/wiki/test_transcript_parser_output.py` | Create | Тесты для `output` поля и `toolResult` матчинга |
| `tests/wiki/test_stats_budget.py` | Create | Тесты для бюджетных секций отчёта |
| `tests/wiki/fixtures/transcripts/with_tool_output.jsonl` | Create | Фикстура транскрипта с toolResult |

---

## Task 1: Добавить `log_context_inject()` в routing_log.py

**Files:**
- Modify: `scripts/wiki/routing_log.py`
- Create: `tests/wiki/test_routing_log_context_inject.py`

- [ ] **Step 1: Написать failing тест**

```python
# tests/wiki/test_routing_log_context_inject.py
from __future__ import annotations
import json
from pathlib import Path
import pytest
import scripts.wiki.routing_log as rl


def test_log_context_inject_writes_jsonl(tmp_path, monkeypatch):
    log = tmp_path / "wiki-usage.jsonl"
    monkeypatch.setattr(rl, "LOG_PATH", log)

    rl.log_context_inject(
        session_id="sess-123",
        source_category="session_start",
        source_label="project_wiki",
        est_tokens=314,
        can_be_wiki=False,
        path="lixiang-dubai3/wiki/index.md",
        model="claude-sonnet-4-6",
    )

    lines = [l for l in log.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "context_inject"
    assert record["source_category"] == "session_start"
    assert record["source_label"] == "project_wiki"
    assert record["est_tokens"] == 314
    assert record["can_be_wiki"] is False
    assert record["path"] == "lixiang-dubai3/wiki/index.md"
    assert record["model"] == "claude-sonnet-4-6"
    assert record["session_id"] == "sess-123"
    assert "ts" in record


def test_log_context_inject_can_be_wiki_true(tmp_path, monkeypatch):
    log = tmp_path / "wiki-usage.jsonl"
    monkeypatch.setattr(rl, "LOG_PATH", log)

    rl.log_context_inject(
        session_id="s1",
        source_category="direct_read",
        source_label="agents/niche-analyst.md",
        est_tokens=800,
        can_be_wiki=True,
    )

    record = json.loads(log.read_text().strip())
    assert record["can_be_wiki"] is True
    assert record["source_category"] == "direct_read"


def test_log_context_inject_optional_fields_default(tmp_path, monkeypatch):
    log = tmp_path / "wiki-usage.jsonl"
    monkeypatch.setattr(rl, "LOG_PATH", log)

    rl.log_context_inject(
        session_id="s1",
        source_category="bash_stdout",
        source_label="gate-check.sh",
        est_tokens=500,
    )

    record = json.loads(log.read_text().strip())
    assert record["path"] == ""
    assert record["model"] == ""
    assert record["can_be_wiki"] is False
```

- [ ] **Step 2: Убедиться что тест падает**

```
pytest tests/wiki/test_routing_log_context_inject.py -v
```

Ожидаем: `AttributeError: module 'scripts.wiki.routing_log' has no attribute 'log_context_inject'`

- [ ] **Step 3: Добавить `log_context_inject()` в routing_log.py**

Открыть `scripts/wiki/routing_log.py`. После строки 91 (конец `log_direct_read`) добавить:

```python
def log_context_inject(
    session_id: str,
    source_category: str,
    source_label: str,
    est_tokens: int,
    can_be_wiki: bool = False,
    path: str = "",
    model: str = "",
) -> None:
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "context_inject",
        "session_id": session_id,
        "model": model,
        "source_category": source_category,
        "source_label": source_label,
        "path": path,
        "est_tokens": est_tokens,
        "can_be_wiki": can_be_wiki,
    })
```

- [ ] **Step 4: Прогнать тесты**

```
pytest tests/wiki/test_routing_log_context_inject.py -v
```

Ожидаем: все 3 PASS.

- [ ] **Step 5: Убедиться что старые тесты не сломались**

```
pytest tests/wiki/test_routing_log.py -v
```

Ожидаем: все PASS.

- [ ] **Step 6: Коммит**

```bash
git add scripts/wiki/routing_log.py tests/wiki/test_routing_log_context_inject.py
git commit -m "feat(wiki): add log_context_inject() to routing_log"
```

---

## Task 2: Расширить transcript_parser — добавить `output` поле и toolResult матчинг

**Files:**
- Modify: `scripts/wiki/transcript_parser.py`
- Create: `tests/wiki/test_transcript_parser_output.py`
- Create: `tests/wiki/fixtures/transcripts/with_tool_output.jsonl`

- [ ] **Step 1: Создать фикстуру транскрипта с toolResult**

```jsonl
{"parentUuid": null, "sessionId": "sess-output-test", "message": {"role": "assistant", "model": "claude-sonnet-4-6", "content": [{"type": "tool_use", "id": "tool-bash-1", "name": "Bash", "input": {"command": "bash scripts/gate-check.sh"}}]}, "type": "assistant", "uuid": "uuid-1", "timestamp": "2026-05-27T10:00:01.000Z"}
{"parentUuid": "uuid-1", "sessionId": "sess-output-test", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "tool-bash-1", "content": [{"type": "text", "text": "Gate check passed: 5/5 checks OK\nStage 07b: approved\nStage 08: pending"}]}]}, "type": "user", "uuid": "uuid-2", "timestamp": "2026-05-27T10:00:02.000Z"}
{"parentUuid": "uuid-2", "sessionId": "sess-output-test", "message": {"role": "assistant", "model": "claude-sonnet-4-6", "content": [{"type": "tool_use", "id": "tool-read-1", "name": "Read", "input": {"file_path": "/d/AI_TEAMS/landing_system/agents/wp-builder.md"}}]}, "type": "assistant", "uuid": "uuid-3", "timestamp": "2026-05-27T10:00:03.000Z"}
{"parentUuid": "uuid-3", "sessionId": "sess-output-test", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "tool-read-1", "content": [{"type": "text", "text": "# wp-builder\n\nBuild WordPress themes..."}]}]}, "type": "user", "uuid": "uuid-4", "timestamp": "2026-05-27T10:00:04.000Z"}
```

Сохранить в `tests/wiki/fixtures/transcripts/with_tool_output.jsonl`.

- [ ] **Step 2: Написать failing тесты**

```python
# tests/wiki/test_transcript_parser_output.py
from __future__ import annotations
from pathlib import Path
import pytest
from scripts.wiki.transcript_parser import extract_tool_calls

FIXTURES = Path(__file__).parent / "fixtures" / "transcripts"


def test_bash_tool_call_has_output():
    calls = extract_tool_calls(FIXTURES / "with_tool_output.jsonl")
    bash_calls = [c for c in calls if c.tool_name == "Bash"]
    assert len(bash_calls) == 1
    assert "Gate check passed" in bash_calls[0].output
    assert "5/5 checks OK" in bash_calls[0].output


def test_read_tool_call_has_output():
    calls = extract_tool_calls(FIXTURES / "with_tool_output.jsonl")
    read_calls = [c for c in calls if c.tool_name == "Read"]
    assert len(read_calls) == 1
    assert "wp-builder" in read_calls[0].output


def test_output_empty_when_no_tool_result(tmp_path):
    transcript = tmp_path / "no_result.jsonl"
    transcript.write_text(
        '{"parentUuid": null, "sessionId": "s1", "message": {"role": "assistant", '
        '"model": "claude-sonnet-4-6", "content": [{"type": "tool_use", "id": "t1", '
        '"name": "Bash", "input": {"command": "ls"}}]}, '
        '"type": "assistant", "uuid": "u1", "timestamp": "2026-05-27T10:00:01.000Z"}\n',
        encoding="utf-8",
    )
    calls = extract_tool_calls(transcript)
    assert len(calls) == 1
    assert calls[0].output == ""
```

- [ ] **Step 3: Убедиться что тесты падают**

```
pytest tests/wiki/test_transcript_parser_output.py -v
```

Ожидаем: `AttributeError: 'ToolCall' object has no attribute 'output'`

- [ ] **Step 4: Расширить `ToolCall` и `extract_tool_calls()` в transcript_parser.py**

Открыть `scripts/wiki/transcript_parser.py`.

Изменить `ToolCall` dataclass (добавить поле `output` после `is_sidechain`):

```python
@dataclass
class ToolCall:
    ts: str
    tool_name: str
    input_params: dict
    session_id: str
    model: str = ""
    thinking_tokens: int = 0
    speed: str = ""
    entrypoint: str = ""
    is_sidechain: bool = False
    output: str = ""          # содержимое toolResult, смонтированное по tool_use_id
```

В `extract_tool_calls()` добавить второй проход для матчинга toolResult. В конце функции, перед `return calls`, добавить:

```python
    # Второй проход: матчим toolResult → tool output
    # Структура: message.content[].type == "tool_result" с tool_use_id
    result_map: dict[str, str] = {}
    for record in records:
        msg = record.get("message", {})
        if msg.get("role") != "user":
            continue
        for block in msg.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_result":
                continue
            tool_use_id = block.get("tool_use_id", "")
            if not tool_use_id:
                continue
            # content может быть строкой или списком блоков
            content = block.get("content", "")
            if isinstance(content, str):
                result_map[tool_use_id] = content
            elif isinstance(content, list):
                parts = [
                    b.get("text", "") for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                ]
                result_map[tool_use_id] = "\n".join(parts)

    # Матчим по id из input-записей транскрипта
    # tool_use id хранится в блоке tool_use в поле "id"
    # Нужно также сохранять id при первом проходе
    for call, tool_id in zip(calls, _tool_ids):
        call.output = result_map.get(tool_id, "")

    return calls
```

Первый проход тоже нужно изменить — собирать `_tool_ids` параллельно с `calls`. В начале функции добавить `_tool_ids: list[str] = []`, в блоке парсинга `tool_use` добавить `_tool_ids.append(block.get("id", ""))`.

Полный рефактор `extract_tool_calls()` (заменить существующую функцию целиком):

```python
def extract_tool_calls(transcript_path: Path) -> list[ToolCall]:
    calls: list[ToolCall] = []
    tool_ids: list[str] = []
    records: list[dict] = []

    for line in transcript_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    for record in records:
        msg = record.get("message", {})
        if msg.get("role") != "assistant":
            continue

        session_id = record.get("sessionId", "")
        ts = record.get("timestamp", "")
        model = msg.get("model", "")
        speed = (msg.get("usage") or {}).get("speed", "")
        entrypoint = record.get("entrypoint", "")
        is_sidechain = bool(record.get("isSidechain", False))

        thinking_tokens = 0
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "thinking":
                thinking_tokens += len(block.get("thinking", "")) // 4

        for block in msg.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            tool_name = block.get("name", "")
            input_params = block.get("input", {})
            tool_id = block.get("id", "")
            calls.append(ToolCall(
                ts=ts,
                tool_name=tool_name,
                input_params=input_params,
                session_id=session_id,
                model=model,
                thinking_tokens=thinking_tokens,
                speed=speed,
                entrypoint=entrypoint,
                is_sidechain=is_sidechain,
                output="",
            ))
            tool_ids.append(tool_id)

    # Второй проход: матчим toolResult → tool output по tool_use_id
    result_map: dict[str, str] = {}
    for record in records:
        msg = record.get("message", {})
        if msg.get("role") != "user":
            continue
        for block in msg.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_result":
                continue
            tool_use_id = block.get("tool_use_id", "")
            if not tool_use_id:
                continue
            content = block.get("content", "")
            if isinstance(content, str):
                result_map[tool_use_id] = content
            elif isinstance(content, list):
                parts = [
                    b.get("text", "") for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                ]
                result_map[tool_use_id] = "\n".join(parts)

    for call, tool_id in zip(calls, tool_ids):
        call.output = result_map.get(tool_id, "")

    return calls
```

- [ ] **Step 5: Прогнать тесты**

```
pytest tests/wiki/test_transcript_parser_output.py -v
```

Ожидаем: все 3 PASS.

- [ ] **Step 6: Убедиться что старые тесты не сломались**

```
pytest tests/wiki/test_transcript_parser.py -v
```

Ожидаем: все PASS (поле `output` — optional с default `""`).

- [ ] **Step 7: Коммит**

```bash
git add scripts/wiki/transcript_parser.py \
        tests/wiki/test_transcript_parser_output.py \
        tests/wiki/fixtures/transcripts/with_tool_output.jsonl
git commit -m "feat(wiki): add output field to ToolCall, match toolResult by tool_use_id"
```

---

## Task 3: Расширить `SOURCE_READ_PATTERNS` в config.py

**Files:**
- Modify: `scripts/wiki/config.py`

- [ ] **Step 1: Найти и заменить SOURCE_READ_PATTERNS**

Открыть `scripts/wiki/config.py`. Найти `SOURCE_READ_PATTERNS` и заменить на:

```python
SOURCE_READ_PATTERNS: list[str] = [
    "agents/*.md",
    "skills/*/SKILL.md",
    "commands/*.md",
    "docs/standards/*.md",
    "docs/**/*.md",
    "template/**/*.md",
    "CLAUDE.md",
    "wiki/**/*.md",
    "memory/**/*.md",
    "skills/*/*.md",
]
```

- [ ] **Step 2: Прогнать существующие тесты config**

```
pytest tests/wiki/test_transcript_parser.py -v -k "source_read"
```

Ожидаем: все PASS (старые паттерны сохранены, новые только добавлены).

- [ ] **Step 3: Коммит**

```bash
git add scripts/wiki/config.py
git commit -m "feat(wiki): expand SOURCE_READ_PATTERNS to cover docs, template, CLAUDE.md"
```

---

## Task 4: Логировать инжекты в session_start.py

**Files:**
- Modify: `scripts/wiki/hooks/session_start.py`

- [ ] **Step 1: Добавить логирование project_wiki и project_memory**

Открыть `scripts/wiki/hooks/session_start.py`. В функции `main()` найти блок где читается `proj_index` и `memory_recent` (строки ~127-142). Добавить вызовы `log_context_inject` сразу после чтения каждого файла.

Изменить блок внутри `if slug:` следующим образом:

```python
    if slug:
        try:
            from scripts.lib.paths import project_dir
            from scripts.wiki import routing_log
            import os
            session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
            model = os.environ.get("CLAUDE_CODE_MODEL", "")

            project = project_dir(slug)
            proj_index_path = project / "wiki" / "index.md"
            proj_index = _read_or_empty(proj_index_path)
            if proj_index:
                chunks.append(
                    f"<project_wiki_index project=\"{slug}\">\n{proj_index}\n</project_wiki_index>"
                )
                try:
                    routing_log.log_context_inject(
                        session_id=session_id,
                        source_category="session_start",
                        source_label="project_wiki",
                        est_tokens=int(len(proj_index) / 3.5),
                        can_be_wiki=False,
                        path=str(proj_index_path),
                        model=model,
                    )
                except Exception:
                    pass

            memory_path = project / "memory"
            memory_recent = _latest_daily(memory_path)
            if memory_recent:
                chunks.append(
                    f"<project_recent_memory project=\"{slug}\">\n{memory_recent}\n</project_recent_memory>"
                )
                try:
                    latest_file = sorted((memory_path / "daily").glob("*.md"))[-1]
                    routing_log.log_context_inject(
                        session_id=session_id,
                        source_category="session_start",
                        source_label="project_memory",
                        est_tokens=int(len(memory_recent) / 3.5),
                        can_be_wiki=False,
                        path=str(latest_file),
                        model=model,
                    )
                except Exception:
                    pass
        except ImportError:
            pass
```

- [ ] **Step 2: Проверить что session_start не падает**

```
echo '{"cwd": "D:/AI_TEAMS/landing_system"}' | python scripts/wiki/hooks/session_start.py
```

Ожидаем: вывод wiki_runtime блока без ошибок.

- [ ] **Step 3: Коммит**

```bash
git add scripts/wiki/hooks/session_start.py
git commit -m "feat(wiki): log context_inject events for project_wiki and project_memory in session_start"
```

---

## Task 5: Логировать framework_load и bash_stdout в flush.py

**Files:**
- Modify: `scripts/wiki/flush.py`

- [ ] **Step 1: Добавить вспомогательную функцию `_extract_script_label()`**

В `flush.py` перед `flush_transcript()` добавить:

```python
def _extract_script_label(command: str) -> str:
    """Извлекает короткий label из bash-команды. Например: 'bash scripts/gate-check.sh arg' → 'gate-check.sh'."""
    import re
    # Ищем .sh файл в команде
    m = re.search(r'([\w\-]+\.sh)', command)
    if m:
        return m.group(1)
    # Fallback: первые 40 символов команды
    return command[:40].strip()
```

- [ ] **Step 2: Добавить логирование framework_load и bash_stdout в `flush_transcript()`**

В `flush.py` найти блок `# Анализ routing` (строки ~86-113). После существующего блока с `log_direct_read` добавить два новых блока:

```python
        # Блок A: framework_load — Skill tool invocations (synthetic)
        SKILL_TOOL_NAMES = {"Skill", "skill", "mcp__claude_ai__skill"}
        COMMAND_TOOL_NAMES = {"mcp__claude_ai__slash_command"}
        for tc in tool_calls:
            if tc.tool_name in SKILL_TOOL_NAMES:
                skill_name = tc.input_params.get("skill", "")
                if not skill_name:
                    continue
                skill_file = _Path(LANDING_SYSTEM) / "skills" / skill_name / "SKILL.md"
                if skill_file.exists():
                    routing_log.log_context_inject(
                        session_id, "framework_load", f"skill:{skill_name}",
                        est_tokens=routing_log.estimate_tokens_file(skill_file),
                        can_be_wiki=False,
                        path=str(skill_file),
                        model=tc.model,
                    )
            elif tc.tool_name in COMMAND_TOOL_NAMES:
                cmd_name = tc.input_params.get("command", "").lstrip("/")
                if not cmd_name:
                    continue
                cmd_file = _Path(LANDING_SYSTEM) / ".claude" / "commands" / f"{cmd_name}.md"
                if cmd_file.exists():
                    routing_log.log_context_inject(
                        session_id, "framework_load", f"command:{cmd_name}",
                        est_tokens=routing_log.estimate_tokens_file(cmd_file),
                        can_be_wiki=False,
                        path=str(cmd_file),
                        model=tc.model,
                    )

        # Блок B: bash_stdout — stdout из Bash tool calls
        TOKEN_THRESHOLD = 100  # игнорировать мелкие выводы
        for tc in tool_calls:
            if tc.tool_name != "Bash":
                continue
            output = tc.output or ""
            est = int(len(output) / 3.5)
            if est <= TOKEN_THRESHOLD:
                continue
            cmd = tc.input_params.get("command", "")
            label = _extract_script_label(cmd)
            routing_log.log_context_inject(
                session_id, "bash_stdout", label,
                est_tokens=est,
                can_be_wiki=False,
                model=tc.model,
            )
```

- [ ] **Step 3: Убедиться что flush.py импортирует нужное**

В начале `flush.py` уже есть `from pathlib import Path as _Path` и `from scripts.wiki import transcript_parser, routing_log`. Проверить что `import re` доступен (он в stdlib, используется в `_extract_script_label`).

- [ ] **Step 4: Проверить синтаксис**

```
python -c "import scripts.wiki.flush; print('ok')"
```

Ожидаем: `ok`

- [ ] **Step 5: Коммит**

```bash
git add scripts/wiki/flush.py
git commit -m "feat(wiki): log framework_load and bash_stdout context_inject events in flush"
```

---

## Task 6: Расширить stats.py — Token Budget секции в отчёте

**Files:**
- Modify: `scripts/wiki/stats.py`
- Create: `tests/wiki/test_stats_budget.py`

- [ ] **Step 1: Написать failing тесты**

```python
# tests/wiki/test_stats_budget.py
from __future__ import annotations
from scripts.wiki.stats import compute_stats, generate_report, one_line_summary, StatsResult


SAMPLE_EVENTS = [
    # wiki_query
    {"ts": "2026-05-27T10:00:00", "type": "wiki_query", "session_id": "s1",
     "model": "claude-sonnet-4-6", "thinking_tokens": 0, "speed": "",
     "entrypoint": "", "is_sidechain": False,
     "filters": {}, "hits": ["landing-build"], "hits_count": 1, "est_tokens_saved": 400},
    # context_inject — session_start
    {"ts": "2026-05-27T10:01:00", "type": "context_inject", "session_id": "s1",
     "model": "claude-sonnet-4-6", "source_category": "session_start",
     "source_label": "project_wiki", "path": "x/wiki/index.md",
     "est_tokens": 314, "can_be_wiki": False},
    # context_inject — framework_load
    {"ts": "2026-05-27T10:02:00", "type": "context_inject", "session_id": "s1",
     "model": "claude-sonnet-4-6", "source_category": "framework_load",
     "source_label": "skill:landing-build", "path": "skills/landing-build/SKILL.md",
     "est_tokens": 1200, "can_be_wiki": False},
    # context_inject — bash_stdout
    {"ts": "2026-05-27T10:03:00", "type": "context_inject", "session_id": "s1",
     "model": "claude-sonnet-4-6", "source_category": "bash_stdout",
     "source_label": "gate-check.sh", "path": "",
     "est_tokens": 500, "can_be_wiki": False},
    # context_inject — direct_read (утечка)
    {"ts": "2026-05-27T10:04:00", "type": "context_inject", "session_id": "s1",
     "model": "claude-sonnet-4-6", "source_category": "direct_read",
     "source_label": "agents/niche-analyst.md", "path": "agents/niche-analyst.md",
     "est_tokens": 800, "can_be_wiki": True},
]


def test_compute_stats_includes_context_inject():
    result = compute_stats(SAMPLE_EVENTS)
    assert result.queries == 1
    assert result.est_tokens_saved == 400
    assert result.context_injects["session_start"] == 314
    assert result.context_injects["framework_load"] == 1200
    assert result.context_injects["bash_stdout"] == 500
    assert result.context_injects["direct_read"] == 800


def test_compute_stats_leaks_only_can_be_wiki():
    result = compute_stats(SAMPLE_EVENTS)
    assert len(result.leaks) == 1
    assert result.leaks[0]["source_label"] == "agents/niche-analyst.md"
    assert result.leaks[0]["est_tokens"] == 800


def test_generate_report_has_budget_section():
    result = compute_stats(SAMPLE_EVENTS)
    report = generate_report(result)
    assert "## Token Budget по категориям" in report
    assert "session_start" in report
    assert "framework_load" in report
    assert "bash_stdout" in report
    assert "CLAUDE.md" in report
    assert "10 231" in report or "10231" in report  # fixed overhead


def test_generate_report_has_leaks_section():
    result = compute_stats(SAMPLE_EVENTS)
    report = generate_report(result)
    assert "## Утечки" in report
    assert "agents/niche-analyst.md" in report


def test_one_line_summary_shows_leak_warning():
    result = compute_stats(SAMPLE_EVENTS)
    summary = one_line_summary(result)
    assert "⚠️" in summary
    assert "800" in summary


def test_one_line_summary_no_warning_when_no_leaks():
    events = [SAMPLE_EVENTS[0]]  # только wiki_query
    result = compute_stats(events)
    summary = one_line_summary(result)
    assert "⚠️" not in summary


def test_old_direct_read_events_counted_as_leaks():
    """Старые direct_read events (без context_inject) тоже учитываются."""
    events = [
        {"ts": "2026-05-27T10:00:00", "type": "direct_read", "session_id": "s1",
         "model": "claude-sonnet-4-6", "thinking_tokens": 0, "speed": "",
         "entrypoint": "", "is_sidechain": False,
         "path": "agents/old-agent.md", "est_tokens": 600, "had_prior_query": False},
    ]
    result = compute_stats(events)
    assert result.direct_reads == 1
    assert result.est_tokens_spent_bypass == 600
    assert len(result.leaks) == 1
    assert result.leaks[0]["source_label"] == "agents/old-agent.md"
```

- [ ] **Step 2: Убедиться что тесты падают**

```
pytest tests/wiki/test_stats_budget.py -v
```

Ожидаем: `AttributeError: 'StatsResult' object has no attribute 'context_injects'`

- [ ] **Step 3: Расширить `StatsResult` в stats.py**

Заменить `StatsResult` dataclass:

```python
@dataclass
class StatsResult:
    queries: int = 0
    direct_reads: int = 0
    est_tokens_saved: int = 0
    est_tokens_spent_bypass: int = 0
    bypass_rate: float = 0.0
    top_bypass: list[dict] = field(default_factory=list)
    by_date: list[dict] = field(default_factory=list)
    by_model: list[dict] = field(default_factory=list)
    # новые поля
    context_injects: dict[str, int] = field(default_factory=dict)  # category → tokens
    leaks: list[dict] = field(default_factory=list)                 # can_be_wiki=True items
```

- [ ] **Step 4: Расширить `compute_stats()` в stats.py**

В `compute_stats()` добавить обработку `context_inject` событий. После блока `for e in events:` добавить сбор `context_injects` и `leaks`:

```python
    # Новые поля для context_inject событий
    inject_map: dict[str, int] = defaultdict(int)   # category → total tokens
    leaks: list[dict] = []

    for e in events:
        ts_str = e.get("ts", "")
        try:
            date_key = ts_str[:10]
        except (TypeError, IndexError):
            date_key = "unknown"

        model = e.get("model") or "unknown"
        thinking = e.get("thinking_tokens", 0)

        if e.get("type") == "wiki_query":
            queries += 1
            est_saved += e.get("est_tokens_saved", 0)
            by_date_map[date_key]["queries"] += 1
            by_date_map[date_key]["est_saved"] += e.get("est_tokens_saved", 0)
            by_model_map[model]["queries"] += 1
            by_model_map[model]["thinking_tokens_total"] += thinking

        elif e.get("type") == "direct_read":
            direct_reads += 1
            est_bypass += e.get("est_tokens", 0)
            path = e.get("path", "unknown")
            bypass_map[path]["count"] += 1
            if e.get("had_prior_query"):
                bypass_map[path]["had_prior_query_count"] += 1
            by_date_map[date_key]["direct_reads"] += 1
            by_model_map[model]["direct_reads"] += 1
            by_model_map[model]["thinking_tokens_total"] += thinking
            # direct_read — всегда утечка
            leaks.append({
                "source_label": path,
                "est_tokens": e.get("est_tokens", 0),
                "had_prior_query": e.get("had_prior_query", False),
            })

        elif e.get("type") == "context_inject":
            category = e.get("source_category", "unknown")
            tokens = e.get("est_tokens", 0)
            inject_map[category] += tokens
            if e.get("can_be_wiki"):
                leaks.append({
                    "source_label": e.get("source_label", ""),
                    "est_tokens": tokens,
                    "had_prior_query": False,
                })
```

В `return StatsResult(...)` добавить новые поля:

```python
    return StatsResult(
        queries=queries,
        direct_reads=direct_reads,
        est_tokens_saved=est_saved,
        est_tokens_spent_bypass=est_bypass,
        bypass_rate=bypass_rate,
        top_bypass=top_bypass,
        by_date=by_date,
        by_model=by_model,
        context_injects=dict(inject_map),
        leaks=leaks,
    )
```

- [ ] **Step 5: Расширить `generate_report()` в stats.py**

В конце функции `generate_report()`, перед `return "\n".join(lines) + "\n"`, добавить:

```python
    # Token Budget по категориям
    CLAUDE_MD_TOKENS = 10_231  # fixed overhead: 35809 bytes / 3.5
    lines += [
        "",
        "## Token Budget по категориям (7д)",
        "",
        "| Категория | Событий | ~Токенов | Можно на вики? |",
        "|-----------|---------|----------|----------------|",
        f"| wiki_query | {stats.queries} | −{stats.est_tokens_saved:,} | — |".replace(",", " "),
    ]

    category_order = ["direct_read", "session_start", "framework_load", "bash_stdout"]
    category_labels = {
        "direct_read": "direct_read",
        "session_start": "session_start",
        "framework_load": "framework_load",
        "bash_stdout": "bash_stdout",
    }
    can_be_wiki_labels = {
        "direct_read": "⚠️ да",
        "session_start": "нет",
        "framework_load": "нет",
        "bash_stdout": "нет",
    }

    # Старые direct_read события (не через context_inject)
    if stats.direct_reads > 0:
        lines.append(
            f"| direct_read (legacy) | {stats.direct_reads} "
            f"| +{stats.est_tokens_spent_bypass:,} | ⚠️ да |".replace(",", " ")
        )

    for cat in category_order:
        tokens = stats.context_injects.get(cat, 0)
        if tokens == 0:
            continue
        label = category_labels.get(cat, cat)
        can_wiki = can_be_wiki_labels.get(cat, "нет")
        lines.append(f"| {label} | — | +{tokens:,} | {can_wiki} |".replace(",", " "))

    lines.append(f"| CLAUDE.md | — | ~{CLAUDE_MD_TOKENS:,} | нет (fixed) |".replace(",", " "))

    # Утечки
    if stats.leaks:
        lines += [
            "",
            "## Утечки — читается напрямую вместо вики",
            "",
            "| Файл | ~Токенов | Агент знал про вики |",
            "|------|----------|---------------------|",
        ]
        for leak in stats.leaks:
            knew = "да ⚠️" if leak.get("had_prior_query") else "нет"
            lines.append(f"| {leak['source_label']} | {leak['est_tokens']} | {knew} |")
```

- [ ] **Step 6: Расширить `one_line_summary()` в stats.py**

Заменить функцию `one_line_summary()`:

```python
def one_line_summary(stats: StatsResult, days: int = 7) -> str:
    bypass_pct = int(stats.bypass_rate * 100)
    saved = f"{stats.est_tokens_saved:,}".replace(",", " ")
    spent = f"{stats.est_tokens_spent_bypass:,}".replace(",", " ")

    # Считаем все токены утечек (direct_read + context_inject с can_be_wiki=True)
    leak_tokens = stats.est_tokens_spent_bypass + sum(
        l["est_tokens"] for l in stats.leaks
        if l.get("source_label", "") not in [b.get("path", "") for b in stats.top_bypass]
    )
    # Проще: считаем по leaks напрямую
    leak_tokens = sum(l["est_tokens"] for l in stats.leaks)

    leak_str = f" · ⚠️ {leak_tokens:,} токенов в обход".replace(",", " ") if leak_tokens > 0 else ""

    return (
        f"Вики-граф ({days}д): {stats.queries} запросов к вики · "
        f"{stats.direct_reads} обходов вики · "
        f"~{saved} токенов сэкономлено · ~{spent} токенов потрачено в обход · "
        f"доля обходов {bypass_pct}%{leak_str}"
    )
```

- [ ] **Step 7: Прогнать все тесты stats**

```
pytest tests/wiki/test_stats_budget.py tests/wiki/test_stats.py -v
```

Ожидаем: все PASS.

- [ ] **Step 8: Коммит**

```bash
git add scripts/wiki/stats.py tests/wiki/test_stats_budget.py
git commit -m "feat(wiki): add Token Budget and Leaks sections to routing-report"
```

---

## Task 7: Финальная проверка — прогнать все wiki тесты и пересобрать отчёт

**Files:** нет изменений.

- [ ] **Step 1: Прогнать полный suite тестов wiki**

```
pytest tests/wiki/ -v
```

Ожидаем: все PASS, ни один существующий тест не сломан.

- [ ] **Step 2: Пересобрать отчёт из текущего лога**

```
python -m scripts.wiki.stats --report --days=7
```

Ожидаем: `Report written to D:\AI_TEAMS\landing_system\wiki\routing-report.md`

- [ ] **Step 3: Проверить что отчёт содержит новые секции**

```
python -c "
content = open('wiki/routing-report.md', encoding='utf-8').read()
assert '## Token Budget' in content, 'Token Budget section missing'
assert 'CLAUDE.md' in content, 'CLAUDE.md fixed overhead missing'
print('OK: все секции присутствуют')
"
```

- [ ] **Step 4: Проверить синтаксис всех изменённых модулей**

```
python -c "import scripts.wiki.routing_log, scripts.wiki.transcript_parser, scripts.wiki.stats, scripts.wiki.flush; print('all imports OK')"
```

- [ ] **Step 5: Финальный коммит**

```bash
git add wiki/routing-report.md
git commit -m "chore(wiki): regenerate routing-report with token budget sections"
```
