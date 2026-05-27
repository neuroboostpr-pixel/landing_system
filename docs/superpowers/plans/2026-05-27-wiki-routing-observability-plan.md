# Wiki Routing Observability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить гибридное логирование wiki routing: активный лог в `query.py` + пассивный парсинг транскрипта в `flush.py` + preflight checks + stats CLI + строка статистики в `session_start`.

**Architecture:** 4 новых модуля (`routing_log`, `transcript_parser`, `stats`, `preflight`) + изменения в 3 существующих файлах (`query.py`, `flush.py`, `session_start.py`). Все модули — stdlib only, pytest без SDK. В финальной задаче — параметризация паттернов и экстракция в переиспользуемый скилл.

**Tech Stack:** Python 3.10+, stdlib only (`json`, `pathlib`, `datetime`, `os`, `fnmatch`), pytest.

---

## Файловая карта

| Файл | Статус | Назначение |
|---|---|---|
| `scripts/wiki/routing_log.py` | CREATE | Запись/чтение `logs/wiki-usage.jsonl`, подсчёт токенов |
| `scripts/wiki/transcript_parser.py` | CREATE | Парсинг tool calls из транскрипта JSONL |
| `scripts/wiki/stats.py` | CREATE | Агрегация событий, CLI, Markdown отчёт |
| `scripts/wiki/preflight.py` | CREATE | Проверка окружения перед стартом |
| `scripts/wiki/query.py` | MODIFY | Вызов routing_log после filter_concepts |
| `scripts/wiki/flush.py` | MODIFY | Анализ транскрипта и лог direct reads |
| `scripts/wiki/hooks/session_start.py` | MODIFY | Preflight + stats строка в wiki_runtime |
| `scripts/wiki/config.py` | MODIFY | Добавить SOURCE_READ_PATTERNS |
| `tests/wiki/test_routing_log.py` | CREATE | 5 тестов |
| `tests/wiki/test_transcript_parser.py` | CREATE | 14 тестов (формат-критичные) |
| `tests/wiki/test_stats.py` | CREATE | 5 тестов |
| `tests/wiki/test_preflight.py` | CREATE | 4 теста |
| `tests/wiki/fixtures/transcripts/normal.jsonl` | CREATE | Fixture: нормальный транскрипт |
| `tests/wiki/fixtures/transcripts/broken.jsonl` | CREATE | Fixture: битые строки |
| `tests/wiki/fixtures/transcripts/string_content.jsonl` | CREATE | Fixture: content как строка |
| `skills/wiki-routing-observability/SKILL.md` | CREATE | Описание скилла |
| `skills/wiki-routing-observability/config.example.yaml` | CREATE | Пример конфига |

---

### Task 1: `routing_log.py` — лог wiki-usage.jsonl

**Files:**
- Create: `scripts/wiki/routing_log.py`
- Create: `tests/wiki/test_routing_log.py`

- [ ] **Step 1: Написать failing тесты**

Создать `tests/wiki/test_routing_log.py`:

```python
"""Tests for scripts/wiki/routing_log.py."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture
def log_path(tmp_path):
    return tmp_path / "logs" / "wiki-usage.jsonl"


@pytest.fixture(autouse=True)
def patch_log_path(log_path, monkeypatch):
    """Перенаправляем LOG_PATH в tmp."""
    import scripts.wiki.routing_log as rl
    monkeypatch.setattr(rl, "LOG_PATH", log_path)


def test_log_query_writes_jsonl(log_path):
    from scripts.wiki.routing_log import log_query
    log_query("sess1", {"stage": "08", "type": "agent"}, ["wp-builder"], 4200)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "wiki_query"
    assert record["session_id"] == "sess1"
    assert record["hits"] == ["wp-builder"]
    assert record["hits_count"] == 1
    assert record["est_tokens_saved"] == 4200
    assert "ts" in record


def test_log_direct_read_writes_jsonl(log_path):
    from scripts.wiki.routing_log import log_direct_read
    log_direct_read("sess1", "agents/wp-builder.md", 3200, had_prior_query=True)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "direct_read"
    assert record["path"] == "agents/wp-builder.md"
    assert record["est_tokens"] == 3200
    assert record["had_prior_query"] is True


def test_read_events_filters_by_days(log_path, monkeypatch):
    from scripts.wiki import routing_log as rl
    log_path.parent.mkdir(parents=True, exist_ok=True)
    old_ts = (datetime.now() - timedelta(days=10)).isoformat(timespec="seconds")
    recent_ts = datetime.now().isoformat(timespec="seconds")
    with log_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"ts": old_ts, "type": "wiki_query", "session_id": "old"}) + "\n")
        f.write(json.dumps({"ts": recent_ts, "type": "wiki_query", "session_id": "new"}) + "\n")
    events = rl.read_events(since_days=7)
    assert len(events) == 1
    assert events[0]["session_id"] == "new"


def test_oserror_does_not_raise(log_path, monkeypatch):
    import scripts.wiki.routing_log as rl
    # Папка не существует и права закрыты — симулируем через monkeypatch
    def broken_open(*a, **kw):
        raise OSError("disk full")
    monkeypatch.setattr(rl, "_open_log", broken_open)
    # Не должно бросать исключение
    rl.log_query("s", {}, [], 0)


def test_estimate_tokens_file(tmp_path):
    from scripts.wiki.routing_log import estimate_tokens_file
    f = tmp_path / "test.md"
    f.write_bytes(b"x" * 400)
    assert estimate_tokens_file(f) == 100  # 400 / 4

    missing = tmp_path / "missing.md"
    assert estimate_tokens_file(missing) == 0
```

- [ ] **Step 2: Запустить тесты, убедиться что падают**

```bash
cd d:/AI_TEAMS/landing_system
python -m pytest tests/wiki/test_routing_log.py -v 2>&1 | head -30
```

Ожидание: `ModuleNotFoundError: No module named 'scripts.wiki.routing_log'`

- [ ] **Step 3: Реализовать `routing_log.py`**

Создать `scripts/wiki/routing_log.py`:

```python
"""Запись и чтение logs/wiki-usage.jsonl.

Единственная точка логирования wiki routing событий.
LOG_PATH можно переопределить через monkeypatch в тестах.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import IO, Any

from scripts.wiki import config

LOG_PATH = config.REPO_ROOT / "logs" / "wiki-usage.jsonl"


def _open_log(mode: str = "a") -> IO[str]:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    return LOG_PATH.open(mode, encoding="utf-8")


def _write(record: dict[str, Any]) -> None:
    try:
        with _open_log("a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[wiki routing_log] failed to write: {e}", file=sys.stderr)


def log_query(
    session_id: str,
    filters: dict[str, str | None],
    hits: list[str],
    est_tokens_saved: int,
) -> None:
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "wiki_query",
        "session_id": session_id,
        "filters": filters,
        "hits": hits,
        "hits_count": len(hits),
        "est_tokens_saved": est_tokens_saved,
    })


def log_direct_read(
    session_id: str,
    path: str,
    est_tokens: int,
    had_prior_query: bool,
) -> None:
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "direct_read",
        "session_id": session_id,
        "path": path,
        "est_tokens": est_tokens,
        "had_prior_query": had_prior_query,
    })


def read_events(since_days: int = 7) -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    cutoff = datetime.now() - timedelta(days=since_days)
    result: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts_str = record.get("ts", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        if ts >= cutoff:
            result.append(record)
    return result


def estimate_tokens_file(path: Path) -> int:
    try:
        return path.stat().st_size // 4
    except OSError:
        return 0


def estimate_tokens_saved(wiki_dir: Path, hits: list[dict[str, Any]]) -> int:
    total = 0
    for c in hits:
        source = c.get("source")
        card = c.get("card")
        if source:
            source_path = config.REPO_ROOT / source
            total += estimate_tokens_file(source_path)
        if card:
            card_path = wiki_dir / card
            total -= estimate_tokens_file(card_path)
    return max(0, total)
```

- [ ] **Step 4: Запустить тесты, убедиться что проходят**

```bash
python -m pytest tests/wiki/test_routing_log.py -v
```

Ожидание: `5 passed`

- [ ] **Step 5: Коммит**

```bash
git add scripts/wiki/routing_log.py tests/wiki/test_routing_log.py
git commit -m "feat(wiki): add routing_log module for wiki-usage.jsonl"
```

---

### Task 2: `transcript_parser.py` — парсер tool calls

**Files:**
- Create: `scripts/wiki/transcript_parser.py`
- Create: `tests/wiki/test_transcript_parser.py`
- Create: `tests/wiki/fixtures/transcripts/normal.jsonl`
- Create: `tests/wiki/fixtures/transcripts/broken.jsonl`
- Create: `tests/wiki/fixtures/transcripts/string_content.jsonl`

- [ ] **Step 1: Создать fixture файлы**

Создать `tests/wiki/fixtures/transcripts/normal.jsonl`:

```jsonl
{"role": "assistant", "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/d/AI_TEAMS/landing_system/agents/wp-builder.md"}}]}
{"role": "assistant", "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "python -m scripts.wiki.query --stage=08 --type=agent"}}]}
{"role": "assistant", "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/d/AI_TEAMS/landing_system/skills/wp-gutenberg-block-builder/SKILL.md"}}]}
{"role": "assistant", "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "python -m scripts.wiki.query --slug=block-composer --format=cards"}}]}
{"role": "assistant", "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/d/AI_TEAMS/landing_system/wiki/concepts/agents/wp-builder.md"}}]}
```

Создать `tests/wiki/fixtures/transcripts/broken.jsonl`:

```jsonl
{"role": "assistant", "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/path/agents/ok.md"}}]}
NOT VALID JSON {{{
{"role": "assistant", "content": [{"type": "tool_use", "name": "Bash"}]}
{"role": "assistant", "content": [{"type": "tool_use", "input": {"file_path": "/path/agents/no-name.md"}}]}
```

Создать `tests/wiki/fixtures/transcripts/string_content.jsonl`:

```jsonl
{"role": "assistant", "content": "plain string content, not a list"}
{"role": "user", "content": "user message"}
```

- [ ] **Step 2: Написать failing тесты**

Создать `tests/wiki/test_transcript_parser.py`:

```python
"""Tests for scripts/wiki/transcript_parser.py.

CRITICAL: эти тесты — первый сигнал при изменении формата транскрипта Claude Code.
При обновлении Claude Code и падении этих тестов — обновить transcript_parser.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "transcripts"


def test_extracts_read_tool_call():
    from scripts.wiki.transcript_parser import extract_tool_calls, ToolCall
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    reads = [tc for tc in tcs if tc.tool_name == "Read"]
    assert len(reads) >= 1
    assert reads[0].input_params["file_path"].endswith("agents/wp-builder.md")


def test_extracts_bash_tool_call():
    from scripts.wiki.transcript_parser import extract_tool_calls
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    bashes = [tc for tc in tcs if tc.tool_name == "Bash"]
    assert len(bashes) >= 1
    assert "scripts.wiki.query" in bashes[0].input_params["command"]


def test_content_as_string_ignored():
    from scripts.wiki.transcript_parser import extract_tool_calls
    tcs = extract_tool_calls(FIXTURES / "string_content.jsonl")
    assert tcs == []


def test_missing_name_field_skipped():
    from scripts.wiki.transcript_parser import extract_tool_calls
    tcs = extract_tool_calls(FIXTURES / "broken.jsonl")
    # Строка без name — пропущена, но строка с name="Read" — должна быть
    names = {tc.tool_name for tc in tcs}
    assert "Read" in names


def test_missing_input_field_skipped():
    from scripts.wiki.transcript_parser import extract_tool_calls
    tcs = extract_tool_calls(FIXTURES / "broken.jsonl")
    # Bash без input — пропускается
    bashes = [tc for tc in tcs if tc.tool_name == "Bash"]
    assert all("command" in tc.input_params or tc.input_params == {} for tc in bashes)


def test_broken_json_line_skipped():
    from scripts.wiki.transcript_parser import extract_tool_calls
    # Не должно бросать исключение
    tcs = extract_tool_calls(FIXTURES / "broken.jsonl")
    assert isinstance(tcs, list)


def test_empty_transcript(tmp_path):
    from scripts.wiki.transcript_parser import extract_tool_calls
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    assert extract_tool_calls(empty) == []


def test_is_source_read_agents():
    from scripts.wiki.transcript_parser import extract_tool_calls, is_source_read
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    agent_reads = [tc for tc in tcs if tc.tool_name == "Read"
                   and "agents/" in tc.input_params.get("file_path", "")
                   and not "wiki/" in tc.input_params.get("file_path", "")]
    assert all(is_source_read(tc) for tc in agent_reads)


def test_is_source_read_skills():
    from scripts.wiki.transcript_parser import extract_tool_calls, is_source_read
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    skill_reads = [tc for tc in tcs if "SKILL.md" in tc.input_params.get("file_path", "")]
    assert all(is_source_read(tc) for tc in skill_reads)


def test_is_source_read_commands(tmp_path):
    from scripts.wiki.transcript_parser import ToolCall, is_source_read
    tc = ToolCall(ts="", tool_name="Read", input_params={"file_path": "/path/commands/landing-go.md"})
    assert is_source_read(tc) is True


def test_is_source_read_wiki_card():
    from scripts.wiki.transcript_parser import extract_tool_calls, is_source_read
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    wiki_reads = [tc for tc in tcs if "wiki/concepts/" in tc.input_params.get("file_path", "")]
    assert all(not is_source_read(tc) for tc in wiki_reads)


def test_is_wiki_query_bash():
    from scripts.wiki.transcript_parser import extract_tool_calls, is_wiki_query
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    query_bashes = [tc for tc in tcs if "scripts.wiki.query" in tc.input_params.get("command", "")]
    assert all(is_wiki_query(tc) for tc in query_bashes)


def test_is_wiki_query_other_bash():
    from scripts.wiki.transcript_parser import ToolCall, is_wiki_query
    tc = ToolCall(ts="", tool_name="Bash", input_params={"command": "git status"})
    assert is_wiki_query(tc) is False


def test_extract_query_slugs():
    from scripts.wiki.transcript_parser import ToolCall, extract_query_slugs
    tc = ToolCall(
        ts="", tool_name="Bash",
        input_params={"command": "python -m scripts.wiki.query --slug=block-composer --format=cards"}
    )
    assert extract_query_slugs(tc) == ["block-composer"]


def test_extract_query_stage():
    from scripts.wiki.transcript_parser import ToolCall, extract_query_stage
    tc = ToolCall(
        ts="", tool_name="Bash",
        input_params={"command": "python -m scripts.wiki.query --stage=08 --type=agent"}
    )
    assert extract_query_stage(tc) == "08"

    tc_no_stage = ToolCall(
        ts="", tool_name="Bash",
        input_params={"command": "python -m scripts.wiki.query --slug=wp-builder"}
    )
    assert extract_query_stage(tc_no_stage) is None
```

- [ ] **Step 3: Запустить тесты, убедиться что падают**

```bash
python -m pytest tests/wiki/test_transcript_parser.py -v 2>&1 | head -20
```

Ожидание: `ModuleNotFoundError: No module named 'scripts.wiki.transcript_parser'`

- [ ] **Step 4: Реализовать `transcript_parser.py`**

Создать `scripts/wiki/transcript_parser.py`:

```python
"""Парсит JSONL транскрипт Claude Code, извлекает tool calls.

ВНИМАНИЕ: самый хрупкий модуль — привязан к формату транскрипта Claude Code.
При обновлении Claude Code сначала смотреть tests/wiki/test_transcript_parser.py.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from scripts.wiki import config


@dataclass
class ToolCall:
    ts: str
    tool_name: str
    input_params: dict = field(default_factory=dict)


def extract_tool_calls(transcript_path: Path) -> list[ToolCall]:
    """Читает JSONL транскрипт, возвращает все tool calls.

    При битой строке или неизвестном формате — пропускает, не бросает.
    """
    result: list[ToolCall] = []
    try:
        text = transcript_path.read_text(encoding="utf-8")
    except OSError:
        return result

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        content = msg.get("content")
        if not isinstance(content, list):
            continue

        ts = msg.get("ts", "")
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            name = block.get("name")
            if not name:
                continue
            input_params = block.get("input")
            if not isinstance(input_params, dict):
                input_params = {}
            result.append(ToolCall(ts=ts, tool_name=name, input_params=input_params))

    return result


def is_source_read(tc: ToolCall) -> bool:
    """True если Read tool с путём из SOURCE_READ_PATTERNS (не wiki карточка)."""
    if tc.tool_name != "Read":
        return False
    path = tc.input_params.get("file_path", "")
    # wiki/concepts/ — это карточки, не bypass
    if "wiki/concepts/" in path or "wiki\\concepts\\" in path:
        return False
    return _matches_source_patterns(path)


def _matches_source_patterns(path: str) -> bool:
    import fnmatch
    for pattern in config.SOURCE_READ_PATTERNS:
        # Нормализуем слэши для кросс-платформенного сравнения
        norm_path = path.replace("\\", "/")
        # Сравниваем только конец пути (без абсолютного префикса)
        if fnmatch.fnmatch(norm_path, f"*/{pattern}") or fnmatch.fnmatch(norm_path, pattern):
            return True
    return False


def is_wiki_query(tc: ToolCall) -> bool:
    """True если Bash tool с 'scripts.wiki.query' в команде."""
    if tc.tool_name != "Bash":
        return False
    command = tc.input_params.get("command", "")
    return "scripts.wiki.query" in command


def get_session_id(transcript_path: Path) -> str:
    """Имя файла транскрипта без расширения."""
    return transcript_path.stem


def extract_query_slugs(tc: ToolCall) -> list[str]:
    """Извлекает значения --slug= из Bash wiki query."""
    command = tc.input_params.get("command", "")
    return re.findall(r"--slug[= ](\S+)", command)


def extract_query_stage(tc: ToolCall) -> str | None:
    """Извлекает значение --stage= из Bash wiki query."""
    command = tc.input_params.get("command", "")
    m = re.search(r"--stage[= ](\S+)", command)
    return m.group(1) if m else None
```

- [ ] **Step 5: Добавить `SOURCE_READ_PATTERNS` в `config.py`**

Открыть `scripts/wiki/config.py` и добавить в конец файла:

```python
# Паттерны путей которые считаются "source reads" (bypass wiki).
# transcript_parser.is_source_read() использует эти паттерны.
# При развёртывании на новом проекте — переопределить под свою структуру.
SOURCE_READ_PATTERNS: list[str] = [
    "agents/*.md",
    "skills/*/SKILL.md",
    "commands/*.md",
    "docs/standards/*.md",
]
```

- [ ] **Step 6: Запустить тесты, убедиться что проходят**

```bash
python -m pytest tests/wiki/test_transcript_parser.py -v
```

Ожидание: `14 passed`

- [ ] **Step 7: Коммит**

```bash
git add scripts/wiki/transcript_parser.py scripts/wiki/config.py \
        tests/wiki/test_transcript_parser.py \
        tests/wiki/fixtures/transcripts/
git commit -m "feat(wiki): add transcript_parser + SOURCE_READ_PATTERNS config"
```

---

### Task 3: `stats.py` — агрегация и отчёт

**Files:**
- Create: `scripts/wiki/stats.py`
- Create: `tests/wiki/test_stats.py`

- [ ] **Step 1: Написать failing тесты**

Создать `tests/wiki/test_stats.py`:

```python
"""Tests for scripts/wiki/stats.py."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest


def _make_events(n_queries=3, n_reads=2, bypass_prior=1):
    """Генерирует синтетические события для тестов."""
    ts = datetime.now().isoformat(timespec="seconds")
    events = []
    for i in range(n_queries):
        events.append({
            "ts": ts, "type": "wiki_query", "session_id": "s1",
            "filters": {"stage": "08"}, "hits": ["wp-builder"],
            "hits_count": 1, "est_tokens_saved": 1000,
        })
    for i in range(n_reads):
        events.append({
            "ts": ts, "type": "direct_read", "session_id": "s1",
            "path": "agents/wp-builder.md", "est_tokens": 800,
            "had_prior_query": i < bypass_prior,
        })
    return events


def test_compute_stats_empty_events():
    from scripts.wiki.stats import compute_stats, StatsResult
    result = compute_stats([])
    assert result.queries == 0
    assert result.direct_reads == 0
    assert result.bypass_rate == 0.0
    assert result.top_bypass == []
    assert result.by_date == []


def test_compute_stats_counts():
    from scripts.wiki.stats import compute_stats
    events = _make_events(n_queries=3, n_reads=2)
    result = compute_stats(events)
    assert result.queries == 3
    assert result.direct_reads == 2
    assert result.est_tokens_saved == 3000
    assert result.est_tokens_spent_bypass == 1600


def test_compute_stats_bypass_rate():
    from scripts.wiki.stats import compute_stats
    events = _make_events(n_queries=3, n_reads=2)
    result = compute_stats(events)
    # bypass_rate = direct_reads / (queries + direct_reads) = 2 / 5 = 0.4
    assert abs(result.bypass_rate - 0.4) < 0.001


def test_compute_stats_top_bypass():
    from scripts.wiki.stats import compute_stats
    events = _make_events(n_queries=2, n_reads=3, bypass_prior=1)
    result = compute_stats(events)
    assert len(result.top_bypass) >= 1
    top = result.top_bypass[0]
    assert top["path"] == "agents/wp-builder.md"
    assert top["count"] == 3
    assert top["had_prior_query_count"] == 1


def test_one_line_summary_format():
    from scripts.wiki.stats import compute_stats, one_line_summary
    events = _make_events(n_queries=23, n_reads=8)
    result = compute_stats(events)
    line = one_line_summary(result)
    assert "queries" in line
    assert "direct reads" in line
    assert "tokens saved" in line
    assert "bypass rate" in line


def test_generate_report_markdown():
    from scripts.wiki.stats import compute_stats, generate_report
    events = _make_events(n_queries=5, n_reads=2)
    result = compute_stats(events)
    md = generate_report(result)
    assert "# Wiki Routing Report" in md
    assert "Топ bypass" in md
    assert "had_prior_query" in md
```

- [ ] **Step 2: Запустить тесты, убедиться что падают**

```bash
python -m pytest tests/wiki/test_stats.py -v 2>&1 | head -20
```

Ожидание: `ModuleNotFoundError: No module named 'scripts.wiki.stats'`

- [ ] **Step 3: Реализовать `stats.py`**

Создать `scripts/wiki/stats.py`:

```python
"""Агрегация wiki routing событий и генерация отчёта.

CLI:
    python -m scripts.wiki.stats              # summary в терминал
    python -m scripts.wiki.stats --report     # пишет wiki/routing-report.md
    python -m scripts.wiki.stats --days=30    # за месяц
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.wiki import config


@dataclass
class StatsResult:
    queries: int = 0
    direct_reads: int = 0
    est_tokens_saved: int = 0
    est_tokens_spent_bypass: int = 0
    bypass_rate: float = 0.0
    top_bypass: list[dict] = field(default_factory=list)
    by_date: list[dict] = field(default_factory=list)


def compute_stats(events: list[dict[str, Any]], since_days: int = 7) -> StatsResult:
    if not events:
        return StatsResult()

    queries = 0
    direct_reads = 0
    est_saved = 0
    est_bypass = 0
    bypass_map: dict[str, dict] = defaultdict(lambda: {"count": 0, "had_prior_query_count": 0})
    by_date_map: dict[str, dict] = defaultdict(
        lambda: {"queries": 0, "direct_reads": 0, "est_saved": 0}
    )

    for e in events:
        ts_str = e.get("ts", "")
        try:
            date_key = ts_str[:10]  # YYYY-MM-DD
        except (TypeError, IndexError):
            date_key = "unknown"

        if e.get("type") == "wiki_query":
            queries += 1
            est_saved += e.get("est_tokens_saved", 0)
            by_date_map[date_key]["queries"] += 1
            by_date_map[date_key]["est_saved"] += e.get("est_tokens_saved", 0)

        elif e.get("type") == "direct_read":
            direct_reads += 1
            est_bypass += e.get("est_tokens", 0)
            path = e.get("path", "unknown")
            bypass_map[path]["count"] += 1
            if e.get("had_prior_query"):
                bypass_map[path]["had_prior_query_count"] += 1
            by_date_map[date_key]["direct_reads"] += 1

    total = queries + direct_reads
    bypass_rate = direct_reads / total if total > 0 else 0.0

    top_bypass = sorted(
        [{"path": k, **v} for k, v in bypass_map.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    by_date = sorted(
        [{"date": k, **v} for k, v in by_date_map.items()],
        key=lambda x: x["date"],
        reverse=True,
    )

    return StatsResult(
        queries=queries,
        direct_reads=direct_reads,
        est_tokens_saved=est_saved,
        est_tokens_spent_bypass=est_bypass,
        bypass_rate=bypass_rate,
        top_bypass=top_bypass,
        by_date=by_date,
    )


def one_line_summary(stats: StatsResult, days: int = 7) -> str:
    bypass_pct = int(stats.bypass_rate * 100)
    saved = f"{stats.est_tokens_saved:,}".replace(",", " ")
    return (
        f"Wiki routing ({days}d): {stats.queries} queries · "
        f"{stats.direct_reads} direct reads · "
        f"~{saved} tokens saved · bypass rate {bypass_pct}%"
    )


def generate_report(stats: StatsResult, since_days: int = 7) -> str:
    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=since_days - 1)
    lines = [
        f"# Wiki Routing Report ({start} — {end})",
        "",
        "| Дата | Queries | Direct reads | Est. saved | Bypass rate |",
        "|------|---------|--------------|------------|-------------|",
    ]
    for row in stats.by_date:
        total = row["queries"] + row["direct_reads"]
        bp = int(row["direct_reads"] / total * 100) if total > 0 else 0
        lines.append(
            f"| {row['date']} | {row['queries']} | {row['direct_reads']} "
            f"| {row['est_saved']:,} t | {bp}% |"
        )
    saved = f"{stats.est_tokens_saved:,}".replace(",", " ")
    bypass_pct = int(stats.bypass_rate * 100)
    lines += [
        "",
        f"**Итого за {since_days} дней:** {stats.queries} queries · "
        f"{stats.direct_reads} direct reads · ~{saved} tokens saved",
        f"**Bypass rate:** {bypass_pct}%",
        "",
        "## Топ bypass файлов",
        "",
        "| Файл | Всего | had_prior_query=true | had_prior_query=false |",
        "|------|-------|----------------------|-----------------------|",
    ]
    for b in stats.top_bypass:
        prior = b["had_prior_query_count"]
        not_prior = b["count"] - prior
        lines.append(f"| {b['path']} | {b['count']} | {prior} | {not_prior} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Wiki routing stats")
    parser.add_argument("--report", action="store_true", help="Write wiki/routing-report.md")
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    from scripts.wiki import routing_log
    events = routing_log.read_events(since_days=args.days)
    result = compute_stats(events, since_days=args.days)

    print(one_line_summary(result, days=args.days))

    if args.report:
        md = generate_report(result, since_days=args.days)
        report_path = config.WIKI_DIR / "routing-report.md"
        report_path.write_text(md, encoding="utf-8")
        print(f"Report written to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Запустить тесты, убедиться что проходят**

```bash
python -m pytest tests/wiki/test_stats.py -v
```

Ожидание: `6 passed`

- [ ] **Step 5: Коммит**

```bash
git add scripts/wiki/stats.py tests/wiki/test_stats.py
git commit -m "feat(wiki): add stats module for routing aggregation and report"
```

---

### Task 4: `preflight.py` — проверка окружения

**Files:**
- Create: `scripts/wiki/preflight.py`
- Create: `tests/wiki/test_preflight.py`

- [ ] **Step 1: Написать failing тесты**

Создать `tests/wiki/test_preflight.py`:

```python
"""Tests for scripts/wiki/preflight.py."""
from __future__ import annotations

import pytest


def test_check_disk_space_ok():
    from scripts.wiki.preflight import check_disk_space
    result = check_disk_space(min_mb=1)
    assert result.ok is True
    assert result.name == "disk_space"


def test_check_logs_dir_writable_missing_dir(tmp_path, monkeypatch):
    from scripts.wiki import preflight, routing_log
    missing = tmp_path / "nonexistent_logs"
    monkeypatch.setattr(routing_log, "LOG_PATH", missing / "wiki-usage.jsonl")
    result = preflight.check_logs_dir_writable()
    # Папка не существует но может быть создана — должно быть ok
    assert result.ok is True


def test_check_index_yaml_missing(tmp_path, monkeypatch):
    from scripts.wiki import preflight, config
    monkeypatch.setattr(config, "WIKI_DIR", tmp_path / "wiki")
    result = preflight.check_index_yaml_exists()
    assert result.ok is False
    assert "index.yaml" in result.message
    assert "compile" in result.fix_hint


def test_run_preflight_returns_all_results():
    from scripts.wiki.preflight import run_preflight, CheckResult
    results = run_preflight()
    assert isinstance(results, list)
    assert all(isinstance(r, CheckResult) for r in results)
    assert len(results) == 4  # disk_space, logs_writable, index_exists, index_parseable
    # run_preflight никогда не бросает исключений
```

- [ ] **Step 2: Запустить тесты, убедиться что падают**

```bash
python -m pytest tests/wiki/test_preflight.py -v 2>&1 | head -20
```

Ожидание: `ModuleNotFoundError: No module named 'scripts.wiki.preflight'`

- [ ] **Step 3: Реализовать `preflight.py`**

Создать `scripts/wiki/preflight.py`:

```python
"""Preflight checks для wiki routing системы.

Вызывается из session_start.py перед логированием.
При failures — блокирует запуск и предлагает fix_hint.
Переопределить через WIKI_PREFLIGHT_SKIP=1.
"""
from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.wiki import config


@dataclass
class CheckResult:
    ok: bool
    name: str
    message: str
    fix_hint: str


def check_disk_space(min_mb: int = 50) -> CheckResult:
    try:
        usage = shutil.disk_usage(config.REPO_ROOT)
        free_mb = usage.free // (1024 * 1024)
        if free_mb < min_mb:
            return CheckResult(
                ok=False,
                name="disk_space",
                message=f"Less than {min_mb}MB free ({free_mb}MB available)",
                fix_hint="Free up disk space",
            )
        return CheckResult(ok=True, name="disk_space", message=f"{free_mb}MB free", fix_hint="")
    except OSError as e:
        return CheckResult(ok=False, name="disk_space", message=str(e), fix_hint="Check disk")


def check_logs_dir_writable() -> CheckResult:
    from scripts.wiki import routing_log
    logs_dir = routing_log.LOG_PATH.parent
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        test_file = logs_dir / ".preflight_write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        return CheckResult(ok=True, name="logs_writable", message=str(logs_dir), fix_hint="")
    except OSError as e:
        return CheckResult(
            ok=False,
            name="logs_writable",
            message=f"logs/ not writable: {logs_dir} ({e})",
            fix_hint=f"mkdir {logs_dir} && check permissions",
        )


def check_index_yaml_exists() -> CheckResult:
    index = config.WIKI_DIR / "index.yaml"
    if index.exists():
        return CheckResult(ok=True, name="index_exists", message=str(index), fix_hint="")
    return CheckResult(
        ok=False,
        name="index_exists",
        message="index.yaml missing",
        fix_hint="python -m scripts.wiki.compile --source-mode=system",
    )


def check_index_yaml_parseable() -> CheckResult:
    index = config.WIKI_DIR / "index.yaml"
    if not index.exists():
        return CheckResult(
            ok=False,
            name="index_parseable",
            message="index.yaml missing (cannot parse)",
            fix_hint="python -m scripts.wiki.compile --source-mode=system",
        )
    try:
        import yaml
        data = yaml.safe_load(index.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "concepts" not in data:
            raise ValueError("missing 'concepts' key")
        return CheckResult(ok=True, name="index_parseable", message="ok", fix_hint="")
    except Exception as e:
        return CheckResult(
            ok=False,
            name="index_parseable",
            message=f"index.yaml parse error: {e}",
            fix_hint="python -m scripts.wiki.compile --source-mode=system",
        )


def run_preflight() -> list[CheckResult]:
    """Запускает все проверки. Никогда не бросает исключений."""
    checks = [
        check_disk_space,
        check_logs_dir_writable,
        check_index_yaml_exists,
        check_index_yaml_parseable,
    ]
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            results.append(CheckResult(
                ok=False,
                name=check.__name__,
                message=f"Unexpected error: {e}",
                fix_hint="Check logs",
            ))
    return results
```

- [ ] **Step 4: Запустить тесты, убедиться что проходят**

```bash
python -m pytest tests/wiki/test_preflight.py -v
```

Ожидание: `4 passed`

- [ ] **Step 5: Коммит**

```bash
git add scripts/wiki/preflight.py tests/wiki/test_preflight.py
git commit -m "feat(wiki): add preflight environment checks"
```

---

### Task 5: Интеграция в `query.py`

**Files:**
- Modify: `scripts/wiki/query.py:125-157`

- [ ] **Step 1: Добавить вызов routing_log в `main()`**

Открыть `scripts/wiki/query.py`. Найти строку `sys.stdout.write(format_output(wiki_dir, concepts, fmt=args.fmt))` (строка ~152) и заменить блок `main()` начиная с `concepts = filter_concepts(...)`:

```python
    concepts = filter_concepts(
        wiki_dir,
        stage=args.stage,
        type_=args.type_,
        tag=args.tag,
        trigger=args.trigger,
        slug=args.slug,
        grep=args.grep,
    )

    # Логируем wiki query (silent если routing_log недоступен)
    try:
        import os
        from scripts.wiki import routing_log
        session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
        filters_dict = {
            "stage": args.stage,
            "type": args.type_,
            "tag": args.tag,
            "trigger": args.trigger,
            "slug": args.slug,
            "grep": args.grep,
        }
        est_saved = routing_log.estimate_tokens_saved(wiki_dir, concepts)
        routing_log.log_query(session_id, filters_dict, [c["slug"] for c in concepts], est_saved)
    except Exception as e:
        print(f"[wiki routing_log] failed to log: {e}", file=sys.stderr)

    sys.stdout.write(format_output(wiki_dir, concepts, fmt=args.fmt))
    return 0
```

- [ ] **Step 2: Проверить что query.py работает без ошибок**

```bash
python -m scripts.wiki.query --type=agent 2>&1 | head -10
```

Ожидание: список агентов без ошибок в stderr.

- [ ] **Step 3: Проверить что лог создался**

```bash
python -m scripts.wiki.query --type=agent --stage=08
# Проверить что появился файл:
python -c "from pathlib import Path; print(list(Path('logs').glob('*.jsonl')))"
```

Ожидание: `[PosixPath('logs/wiki-usage.jsonl')]` (или WindowsPath).

- [ ] **Step 4: Коммит**

```bash
git add scripts/wiki/query.py
git commit -m "feat(wiki): log wiki queries to routing_log from query.py"
```

---

### Task 6: Интеграция в `flush.py`

**Files:**
- Modify: `scripts/wiki/flush.py:71-118`

- [ ] **Step 1: Добавить анализ routing в `flush_transcript()`**

Открыть `scripts/wiki/flush.py`. Найти конец функции `flush_transcript()` после строки `f.write("\n")` и добавить блок:

```python
    # Анализ routing: детектим direct reads (bypass wiki)
    try:
        from pathlib import Path as _Path
        from scripts.wiki import transcript_parser, routing_log
        tool_calls = transcript_parser.extract_tool_calls(transcript_path)
        session_id = transcript_parser.get_session_id(transcript_path)

        queried_slugs: set[str] = set()
        queried_stages: set[str] = set()
        for tc in tool_calls:
            if transcript_parser.is_wiki_query(tc):
                queried_slugs.update(transcript_parser.extract_query_slugs(tc))
                stage = transcript_parser.extract_query_stage(tc)
                if stage:
                    queried_stages.add(stage)

        for tc in tool_calls:
            if transcript_parser.is_source_read(tc):
                path = tc.input_params.get("file_path", "")
                slug = _Path(path).stem
                had_prior = slug in queried_slugs or bool(queried_stages)
                est = routing_log.estimate_tokens_file(_Path(path))
                routing_log.log_direct_read(session_id, path, est, had_prior)
    except Exception as e:
        pass  # silent — мы в фоне
```

- [ ] **Step 2: Убедиться что flush.py импортируется без ошибок**

```bash
python -c "import scripts.wiki.flush; print('ok')"
```

Ожидание: `ok`

- [ ] **Step 3: Коммит**

```bash
git add scripts/wiki/flush.py
git commit -m "feat(wiki): detect source bypasses in flush.py via transcript_parser"
```

---

### Task 7: Интеграция в `session_start.py`

**Files:**
- Modify: `scripts/wiki/hooks/session_start.py:32-57`

- [ ] **Step 1: Обновить `_system_wiki_hint()`**

Открыть `scripts/wiki/hooks/session_start.py`. Заменить всю функцию `_system_wiki_hint()`:

```python
def _system_wiki_hint(cwd: Path) -> str:
    """Preflight + 50-token hint + stats строка.

    Только если CWD находится внутри LANDING_SYSTEM.
    """
    import os
    try:
        cwd.resolve().relative_to(LANDING_SYSTEM)
    except ValueError:
        return ""

    index_yaml = LANDING_SYSTEM / "wiki" / "index.yaml"
    if not index_yaml.exists():
        return ""

    # Preflight checks
    if not os.environ.get("WIKI_PREFLIGHT_SKIP"):
        try:
            sys.path.insert(0, str(LANDING_SYSTEM))
            from scripts.wiki.preflight import run_preflight
            failures = [r for r in run_preflight() if not r.ok]
            if failures:
                lines = ["⚠️  Wiki preflight failed:"]
                for f in failures:
                    lines.append(f"  - {f.message}")
                    lines.append(f"    Fix: {f.fix_hint}")
                lines.append("Set WIKI_PREFLIGHT_SKIP=1 to bypass and continue without logging.")
                return "<wiki_runtime>\n" + "\n".join(lines) + "\n</wiki_runtime>"
        except Exception:
            pass  # если preflight сам упал — не блокируем

    try:
        import yaml
        data = yaml.safe_load(index_yaml.read_text(encoding="utf-8")) or {}
    except Exception:
        return ""
    total = (data.get("counts") or {}).get("total", "?")

    # Stats строка
    stats_line = "Wiki routing (7d): no data yet"
    try:
        from scripts.wiki import routing_log, stats as wiki_stats
        events = routing_log.read_events(since_days=7)
        if events:
            s = wiki_stats.compute_stats(events)
            stats_line = wiki_stats.one_line_summary(s)
    except Exception:
        pass

    return (
        "<wiki_runtime>\n"
        f"Landing-system wiki: {total} concepts indexed at wiki/index.yaml.\n"
        "Query: python -m scripts.wiki.query --stage=N --type=T --tag=X --slug=Y\n"
        "Read card: cat wiki/concepts/<dir>/<slug>.md\n"
        f"{stats_line}\n"
        "</wiki_runtime>"
    )
```

- [ ] **Step 2: Запустить session_start вручную, проверить вывод**

```bash
echo '{"cwd": "d:/AI_TEAMS/landing_system"}' | python scripts/wiki/hooks/session_start.py
```

Ожидание: вывод содержит `<wiki_runtime>` с 5 строками включая stats line.

- [ ] **Step 3: Коммит**

```bash
git add scripts/wiki/hooks/session_start.py
git commit -m "feat(wiki): add preflight + stats line to session_start wiki_runtime hint"
```

---

### Task 8: Gitignore + полный прогон тестов

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Добавить в `.gitignore`**

Открыть `.gitignore` и добавить:

```
logs/wiki-usage.jsonl
wiki/routing-report.md
```

- [ ] **Step 2: Запустить все новые тесты**

```bash
python -m pytest tests/wiki/test_routing_log.py tests/wiki/test_transcript_parser.py tests/wiki/test_stats.py tests/wiki/test_preflight.py -v
```

Ожидание: `28 passed` (5+14+6+4 — без учёта pre-existing failures в других тестах).

- [ ] **Step 3: Проверить что старые wiki тесты не сломались**

```bash
python -m pytest tests/wiki/ -v --ignore=tests/wiki/test_routing_log.py --ignore=tests/wiki/test_transcript_parser.py --ignore=tests/wiki/test_stats.py --ignore=tests/wiki/test_preflight.py 2>&1 | tail -20
```

Ожидание: те же результаты что и до этого PR (pre-existing failures не ухудшились).

- [ ] **Step 4: Коммит**

```bash
git add .gitignore
git commit -m "chore: gitignore wiki-usage.jsonl and routing-report.md"
```

---

### Task 9: Скилл `wiki-routing-observability`

**Files:**
- Create: `skills/wiki-routing-observability/SKILL.md`
- Create: `skills/wiki-routing-observability/config.example.yaml`
- Add test: `tests/wiki/test_transcript_parser.py` — один новый тест

- [ ] **Step 1: Добавить тест на параметризацию паттернов**

Открыть `tests/wiki/test_transcript_parser.py` и добавить в конец:

```python
def test_source_read_uses_config_patterns(monkeypatch):
    """При изменении SOURCE_READ_PATTERNS — is_source_read отражает новый конфиг."""
    from scripts.wiki import config as wiki_config
    from scripts.wiki.transcript_parser import ToolCall, is_source_read

    monkeypatch.setattr(wiki_config, "SOURCE_READ_PATTERNS", ["custom/*.md"])
    tc_custom = ToolCall(ts="", tool_name="Read", input_params={"file_path": "/root/custom/foo.md"})
    tc_agent = ToolCall(ts="", tool_name="Read", input_params={"file_path": "/root/agents/bar.md"})

    assert is_source_read(tc_custom) is True
    assert is_source_read(tc_agent) is False
```

- [ ] **Step 2: Запустить новый тест**

```bash
python -m pytest tests/wiki/test_transcript_parser.py::test_source_read_uses_config_patterns -v
```

Ожидание: `PASSED` — `_matches_source_patterns` уже читает `config.SOURCE_READ_PATTERNS` из Task 2. Если FAILED — проверь что в `transcript_parser.py` нет хардкода паттернов.

- [ ] **Step 3: Создать `skills/wiki-routing-observability/SKILL.md`**

```bash
mkdir -p skills/wiki-routing-observability
```

Создать `skills/wiki-routing-observability/SKILL.md`:

```markdown
---
name: wiki-routing-observability
description: Hybrid logging for wiki routing systems — tracks wiki queries vs direct source reads, estimates token savings, preflight checks. Reusable across any project with a wiki/index.yaml.
---

# wiki-routing-observability

Переиспользуемый скилл для измерения эффективности wiki routing.

## Что делает

- Логирует каждый `query.py` вызов → `logs/wiki-usage.jsonl`
- На session end парсит транскрипт → детектит прямые чтения исходников (bypass)
- `session_start` показывает stats строку: queries / direct reads / tokens saved / bypass rate
- `python -m scripts.wiki.stats --report` → `wiki/routing-report.md`

## Компоненты

| Файл | Назначение |
|---|---|
| `scripts/routing_log.py` | Запись/чтение JSONL лога |
| `scripts/transcript_parser.py` | Парсинг tool calls из транскрипта |
| `scripts/stats.py` | Агрегация и Markdown отчёт |
| `scripts/preflight.py` | Проверка окружения |

## Развёртывание на новом проекте

1. Скопировать этот скилл в новый проект
2. В `config.yaml` задать `source_read_patterns`:
   ```yaml
   source_read_patterns:
     - "agents/*.md"
     - "skills/*/SKILL.md"
   ```
3. В `session_start.py` добавить вызов preflight + stats (3 строки — см. пример)
4. В `query.py` добавить вызов `routing_log.log_query()` после filter

## Требования

- Python 3.10+, stdlib only
- `wiki/index.yaml` должен существовать
- `logs/` должна быть writable (создаётся автоматически)
```

- [ ] **Step 4: Создать `skills/wiki-routing-observability/config.example.yaml`**

Создать `skills/wiki-routing-observability/config.example.yaml`:

```yaml
# Конфиг wiki-routing-observability для нового проекта.
# Скопируй в config/wiki-observability.yaml и настрой под свою структуру.

# Паттерны путей которые считаются "source reads" (bypass wiki).
# Используются transcript_parser.is_source_read().
source_read_patterns:
  - "agents/*.md"           # агенты pipeline
  - "skills/*/SKILL.md"     # скиллы
  - "commands/*.md"         # slash-команды

# Минимальный свободный диск для логирования (MB).
min_disk_mb: 50

# Количество дней в stats строке session_start.
stats_days: 7
```

- [ ] **Step 5: Запустить полный тест-сьют новых тестов**

```bash
python -m pytest tests/wiki/test_routing_log.py tests/wiki/test_transcript_parser.py tests/wiki/test_stats.py tests/wiki/test_preflight.py -v
```

Ожидание: `29 passed` (добавился 1 новый тест из Step 1).

- [ ] **Step 6: Коммит**

```bash
git add skills/wiki-routing-observability/ tests/wiki/test_transcript_parser.py
git commit -m "feat(wiki): add wiki-routing-observability reusable skill"
```

---

### Task 10: Финальная проверка и smoke test

**Files:** нет новых файлов.

- [ ] **Step 1: Запустить полный прогон всех wiki тестов**

```bash
python -m pytest tests/wiki/ -v 2>&1 | tail -30
```

Ожидание: все 29 новых тестов проходят. Pre-existing failures (если были) не ухудшились.

- [ ] **Step 2: Smoke test — query + stats**

```bash
python -m scripts.wiki.query --type=agent --stage=08
python -m scripts.wiki.stats
```

Ожидание: query возвращает агентов, stats показывает `Wiki routing (7d): 1 queries · 0 direct reads · ...`

- [ ] **Step 3: Smoke test — session_start**

```bash
echo '{"cwd": "d:/AI_TEAMS/landing_system"}' | python scripts/wiki/hooks/session_start.py
```

Ожидание: `<wiki_runtime>` с 5 строками, последняя — stats line с числами.

- [ ] **Step 4: Финальный коммит**

```bash
git add -A
git status  # проверить что нет лишнего
git commit -m "chore(wiki): wiki routing observability complete"
```
