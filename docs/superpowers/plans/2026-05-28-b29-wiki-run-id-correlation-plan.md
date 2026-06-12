# B29 — Wiki Run ID Correlation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Устранить ложные утечки в routing-report — все запуски агентов через субагентов показывают `via_wiki = false` потому что субагент имеет другой `session_id`.

**Architecture:** Новый модуль `scripts/wiki/run_id.py` читает/создаёт файл `.wiki-run-id` с уникальным `run_id` (`landing-YYYYMMDD-HHMM`). `log.py` использует его как fallback для `--session-id`. `stats.py` добавляет сводку по запускам и колонку `run_id` в детализацию. Агенты не меняются.

**Tech Stack:** Python 3.10+, pytest, Markdown.

**Зависимости:** нет.

---

## File Structure

**Создать:**
- `scripts/wiki/run_id.py` — утилита `get_or_create()`, `get()`, `reset()`
- `tests/wiki/test_run_id.py` — тесты для run_id.py

**Изменить:**
- `scripts/wiki/log.py` — fallback: `--session-id` → `.wiki-run-id` → `CLAUDE_SESSION_ID` → `"unknown"`
- `scripts/wiki/stats.py` — новая секция "Запуски (сводка)" + колонка `run_id` в детализации
- `.gitignore` (корневой) — добавить `.wiki-run-id`

---

## Task 1: Модуль `run_id.py`

**Files:**
- Create: `scripts/wiki/run_id.py`
- Test: `tests/wiki/test_run_id.py`

- [ ] **Step 1: Написать failing тесты**

```python
# tests/wiki/test_run_id.py
from __future__ import annotations
import pytest
from pathlib import Path


@pytest.fixture
def run_id_path(tmp_path, monkeypatch):
    p = tmp_path / ".wiki-run-id"
    import scripts.wiki.run_id as rid
    monkeypatch.setattr(rid, "RUN_ID_PATH", p)
    return p


def test_get_returns_none_if_no_file(run_id_path):
    from scripts.wiki.run_id import get
    assert get() is None


def test_get_or_create_creates_file(run_id_path):
    from scripts.wiki.run_id import get_or_create
    result = get_or_create()
    assert run_id_path.exists()
    assert result.startswith("landing-")


def test_get_or_create_returns_same_id_on_second_call(run_id_path):
    from scripts.wiki.run_id import get_or_create
    first = get_or_create()
    second = get_or_create()
    assert first == second


def test_get_reads_existing_file(run_id_path):
    from scripts.wiki.run_id import get
    run_id_path.write_text("landing-20260528-1721", encoding="utf-8")
    assert get() == "landing-20260528-1721"


def test_reset_generates_new_id(run_id_path):
    from scripts.wiki.run_id import get_or_create, reset
    first = get_or_create()
    import time; time.sleep(0.01)
    second = reset()
    assert second != first
    assert run_id_path.read_text(encoding="utf-8") == second


def test_run_id_format(run_id_path):
    from scripts.wiki.run_id import get_or_create
    result = get_or_create()
    # landing-YYYYMMDD-HHMM
    import re
    assert re.match(r"landing-\d{8}-\d{4}", result), f"Bad format: {result}"
```

- [ ] **Step 2: Запустить — убедиться FAIL**

```bash
python -m pytest tests/wiki/test_run_id.py -v
```

Ожидаем: `ModuleNotFoundError` или `ImportError`.

- [ ] **Step 3: Создать `scripts/wiki/run_id.py`**

```python
"""Управление run_id для wiki routing корреляции.

run_id — идентификатор одного рабочего запуска (один /landing-go или ручной старт).
Хранится в .wiki-run-id в корне репо. Новый запуск = reset().
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from scripts.wiki import config

RUN_ID_PATH = config.REPO_ROOT / ".wiki-run-id"


def _generate() -> str:
    return "landing-" + datetime.now().strftime("%Y%m%d-%H%M")


def get() -> str | None:
    """Читает run_id из файла. None если файла нет."""
    try:
        return RUN_ID_PATH.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def get_or_create() -> str:
    """Читает run_id если файл есть, иначе генерирует новый и записывает."""
    existing = get()
    if existing:
        return existing
    return reset()


def reset() -> str:
    """Генерирует новый run_id, перезаписывает файл. Возвращает новый id."""
    new_id = _generate()
    RUN_ID_PATH.write_text(new_id, encoding="utf-8")
    return new_id
```

- [ ] **Step 4: Запустить тесты — убедиться PASS**

```bash
python -m pytest tests/wiki/test_run_id.py -v
```

Ожидаем: 6 тестов PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/run_id.py tests/wiki/test_run_id.py
git commit -m "feat(b29): add run_id module for wiki routing correlation"
```

---

## Task 2: Обновить `log.py` — fallback на `.wiki-run-id`

**Files:**
- Modify: `scripts/wiki/log.py`
- Test: `tests/wiki/test_run_id.py` (добавить тест интеграции с log.py)

- [ ] **Step 1: Написать failing тест**

Добавить в `tests/wiki/test_run_id.py`:

```python
def test_log_py_uses_run_id_when_no_session_id(tmp_path, monkeypatch):
    """log.py берёт session_id из .wiki-run-id если --session-id не передан."""
    import scripts.wiki.run_id as rid
    import scripts.wiki.routing_log as rl

    run_id_file = tmp_path / ".wiki-run-id"
    run_id_file.write_text("landing-20260528-1721", encoding="utf-8")
    monkeypatch.setattr(rid, "RUN_ID_PATH", run_id_file)

    log_path = tmp_path / "logs" / "wiki-usage.jsonl"
    monkeypatch.setattr(rl, "LOG_PATH", log_path)
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

    import scripts.wiki.log as log_mod
    log_mod.main(["log.py", "--type", "agent_call", "--agent", "brand-architect", "--stage", "04"])

    import json
    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["session_id"] == "landing-20260528-1721"
```

- [ ] **Step 2: Запустить — убедиться FAIL**

```bash
python -m pytest tests/wiki/test_run_id.py::test_log_py_uses_run_id_when_no_session_id -v
```

Ожидаем: FAIL — session_id будет `"unknown"`, не `"landing-20260528-1721"`.

- [ ] **Step 3: Изменить `scripts/wiki/log.py`**

Найти строку:
```python
session_id = args.session_id or os.environ.get("CLAUDE_SESSION_ID", "unknown")
```

Заменить на:
```python
from scripts.wiki import run_id as _run_id
session_id = (
    args.session_id
    or _run_id.get_or_create()
    or os.environ.get("CLAUDE_SESSION_ID", "unknown")
)
```

- [ ] **Step 4: Запустить тесты — убедиться PASS**

```bash
python -m pytest tests/wiki/test_run_id.py -v
```

Ожидаем: все 7 тестов PASS.

- [ ] **Step 5: Убедиться что существующие тесты log.py не сломались**

```bash
python -m pytest tests/wiki/test_routing_log.py tests/wiki/test_stats.py -v
```

Ожидаем: все PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/wiki/log.py tests/wiki/test_run_id.py
git commit -m "feat(b29): log.py uses .wiki-run-id as session_id fallback"
```

---

## Task 3: Добавить `.wiki-run-id` в `.gitignore`

**Files:**
- Modify: `.gitignore` (корневой)

- [ ] **Step 1: Добавить строку**

Открыть `.gitignore` в корне репо и добавить:
```
.wiki-run-id
```

- [ ] **Step 2: Убедиться что файл игнорируется**

```bash
echo "landing-20260528-1721" > .wiki-run-id
git status
```

Ожидаем: `.wiki-run-id` НЕ появляется в `Untracked files`.

Удалить тестовый файл:
```bash
rm .wiki-run-id
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore(b29): add .wiki-run-id to .gitignore"
```

---

## Task 4: Обновить `stats.py` — сводка по запускам + колонка run_id

**Files:**
- Modify: `scripts/wiki/stats.py`
- Test: `tests/wiki/test_stats.py` (добавить тесты)

- [ ] **Step 1: Написать failing тесты**

Добавить в `tests/wiki/test_stats.py`:

```python
def test_compute_stats_groups_by_run_id():
    from scripts.wiki.stats import compute_stats
    events = [
        {
            "ts": "2026-05-28T17:21:00",
            "type": "wiki_query",
            "session_id": "landing-20260528-1721",
            "filters": {"stage": "04"},
            "hits": ["brand-architect"],
            "hits_count": 1,
            "est_tokens_saved": 1000,
        },
        {
            "ts": "2026-05-28T17:22:00",
            "type": "agent_call",
            "session_id": "landing-20260528-1721",
            "agent": "brand-architect",
            "stage": "04",
            "via_wiki": True,
        },
        {
            "ts": "2026-05-28T17:51:00",
            "type": "agent_call",
            "session_id": "landing-20260528-1721",
            "agent": "design-system-generator",
            "stage": "05",
            "via_wiki": False,
        },
    ]
    result = compute_stats(events)
    assert len(result.run_summaries) == 1
    summary = result.run_summaries[0]
    assert summary["run_id"] == "landing-20260528-1721"
    assert summary["total"] == 2
    assert summary["via_wiki"] == 1
    assert summary["leaks"] == 1


def test_render_report_includes_run_summary():
    from scripts.wiki.stats import compute_stats, render_report
    events = [
        {
            "ts": "2026-05-28T17:22:00",
            "type": "agent_call",
            "session_id": "landing-20260528-1721",
            "agent": "brand-architect",
            "stage": "04",
            "via_wiki": True,
        },
    ]
    result = compute_stats(events)
    report = render_report(result, since_days=7)
    assert "Запуски (сводка)" in report
    assert "landing-20260528-1721" in report


def test_render_report_launches_table_has_run_id_column():
    from scripts.wiki.stats import compute_stats, render_report
    events = [
        {
            "ts": "2026-05-28T17:22:00",
            "type": "agent_call",
            "session_id": "landing-20260528-1721",
            "agent": "brand-architect",
            "stage": "04",
            "via_wiki": True,
        },
    ]
    result = compute_stats(events)
    report = render_report(result, since_days=7)
    assert "run_id" in report
    assert "20260528-1721" in report
```

- [ ] **Step 2: Запустить — убедиться FAIL**

```bash
python -m pytest tests/wiki/test_stats.py::test_compute_stats_groups_by_run_id tests/wiki/test_stats.py::test_render_report_includes_run_summary tests/wiki/test_stats.py::test_render_report_launches_table_has_run_id_column -v
```

Ожидаем: FAIL — `StatsResult` не имеет `run_summaries`.

- [ ] **Step 3: Добавить `run_summaries` в `StatsResult`**

В `stats.py` найти класс `StatsResult` и добавить поле:

```python
run_summaries: list[dict] = field(default_factory=list)  # per run_id: run_id/date/total/via_wiki/leaks
```

- [ ] **Step 4: Добавить агрегацию по run_id в `compute_stats`**

В функции `compute_stats` после цикла по событиям (перед `return StatsResult(...)`) добавить:

```python
    # Группировка по run_id
    run_map: dict[str, dict] = {}
    for e in events:
        if e.get("type") not in ("stage_start", "agent_call", "skill_call"):
            continue
        rid = e.get("session_id") or "unknown"
        if rid not in run_map:
            run_map[rid] = {
                "run_id": rid,
                "date": e.get("ts", "")[:16].replace("T", " "),
                "total": 0,
                "via_wiki": 0,
                "leaks": 0,
            }
        run_map[rid]["total"] += 1
        if e.get("via_wiki"):
            run_map[rid]["via_wiki"] += 1
        else:
            run_map[rid]["leaks"] += 1
    run_summaries = sorted(run_map.values(), key=lambda x: x["date"], reverse=True)
```

И добавить `run_summaries=run_summaries` в вызов `return StatsResult(...)`.

- [ ] **Step 5: Обновить `render_report` — добавить секцию сводки**

В функции `render_report` (или аналогичной функции генерации markdown) найти блок `if stats.launches:` и добавить ПЕРЕД ним секцию сводки:

```python
    if stats.run_summaries:
        lines.append("\n## Запуски (сводка)\n")
        lines.append("| run_id | Дата | Агентов/этапов | Через вики | Утечки |")
        lines.append("|--------|------|----------------|------------|--------|")
        for s in stats.run_summaries:
            lines.append(
                f"| {s['run_id']} | {s['date']} | {s['total']} "
                f"| {s['via_wiki']} | {s['leaks']} |"
            )
```

- [ ] **Step 6: Обновить таблицу детализации — добавить колонку `run_id`**

Найти блок:
```python
        lines.append("| Время | Тип | Имя | Stage | via_wiki | Утечка? |")
        lines.append("|-------|-----|-----|-------|----------|---------|")
        for e in stats.launches:
            ...
            lines.append(f"| {ts} | {tname} | {name} | {stage} | {via} | {leak} |")
```

Заменить на:
```python
        lines.append("| Время | run_id | Тип | Имя | Stage | via_wiki | Утечка? |")
        lines.append("|-------|--------|-----|-----|-------|----------|---------|")
        for e in stats.launches:
            ts_str = e.get("ts", "")
            ts = ts_str[11:16] if len(ts_str) >= 16 else ts_str
            etype = e.get("type", "")
            if etype == "stage_start":
                name = e.get("stage", "")
                tname = "stage"
            elif etype == "agent_call":
                name = e.get("agent", "")
                tname = "agent"
            else:
                name = e.get("skill", "")
                tname = "skill"
            stage = e.get("stage", "")
            via = "✅" if e.get("via_wiki") else "❌"
            leak = "⚠️" if not e.get("via_wiki") else ""
            # run_id показывается сокращённо: без префикса "landing-"
            rid = e.get("session_id", "")
            rid_short = rid.replace("landing-", "") if rid.startswith("landing-") else rid
            lines.append(f"| {ts} | {rid_short} | {tname} | {name} | {stage} | {via} | {leak} |")
```

- [ ] **Step 7: Запустить тесты — убедиться PASS**

```bash
python -m pytest tests/wiki/test_stats.py -v
```

Ожидаем: все тесты PASS включая 3 новых.

- [ ] **Step 8: Commit**

```bash
git add scripts/wiki/stats.py tests/wiki/test_stats.py
git commit -m "feat(b29): add run_id grouping and column to routing report"
```

---

## Task 5: Обновить бэклог — отметить B29 как реализованный

**Files:**
- Modify: `docs/BACKLOG.md`

- [ ] **Step 1: Добавить ссылки на спек и план в запись B29**

Найти строку `### B29.` в `docs/BACKLOG.md` и добавить в заголовок ссылки:

```markdown
### B29. Wiki-корреляция всегда ложная при запуске через субагентов ✏️ [spec](superpowers/specs/2026-05-28-b29-wiki-run-id-correlation-design.md) [plan](superpowers/plans/2026-05-28-b29-wiki-run-id-correlation-plan.md)
```

- [ ] **Step 2: Обновить строку прогресса**

Найти в секции `## Прогресс`:
```
- 🔮 B5–B20, B29 — по мере роста системы
```

Заменить на:
```
- ✅ B29 — реализован (wiki run_id корреляция)
- 🔮 B5–B20 — по мере роста системы
```

- [ ] **Step 3: Commit**

```bash
git add docs/BACKLOG.md
git commit -m "chore(b29): mark B29 spec+plan links in backlog"
```

---

## Self-Review

**Spec coverage B29:**
- ✅ `run_id.py` с `get_or_create()`, `get()`, `reset()` → Task 1
- ✅ `log.py` fallback на `.wiki-run-id` → Task 2
- ✅ `.wiki-run-id` в `.gitignore` → Task 3
- ✅ Сводка по запускам в отчёте → Task 4
- ✅ Колонка `run_id` в детализации → Task 4
- ✅ Агенты не меняются → `log.py` сам подхватывает

**Placeholder scan:** нет TBD/TODO.

**Type consistency:** `run_summaries: list[dict]` совпадает в `StatsResult`, `compute_stats` и тестах. `get_or_create() -> str`, `get() -> str | None`, `reset() -> str` — сигнатуры совпадают в реализации и тестах.
