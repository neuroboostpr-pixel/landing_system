# Wiki Stage/Agent/Skill Tracking — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить логирование запусков этапов/агентов/скилов с автоматической корреляцией `via_wiki` для выявления утечек токенов.

**Architecture:** Новые функции в `routing_log.py` (`was_wiki_queried`, `log_stage_start`, `log_agent_call`, `log_skill_call`), новый CLI `scripts/wiki/log.py`, интеграция в `gate-check.sh` и ключевые агенты, расширение отчёта в `stats.py`.

**Tech Stack:** Python 3.10+ stdlib, bash, pytest/bats.

---

### Task 1: `was_wiki_queried()` + новые log функции в `routing_log.py`

**Files:**
- Modify: `scripts/wiki/routing_log.py`
- Test: `tests/wiki/test_launch_tracking.py`

- [ ] **Step 1: Написать failing тесты**

Создать `tests/wiki/test_launch_tracking.py`:

```python
"""Tests for stage/agent/skill launch tracking with via_wiki correlation."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.wiki import routing_log


@pytest.fixture(autouse=True)
def tmp_log(tmp_path, monkeypatch):
    log_file = tmp_path / "wiki-usage.jsonl"
    monkeypatch.setattr(routing_log, "LOG_PATH", log_file)
    return log_file


def _write_query(tmp_log: Path, session_id: str, stage: str) -> None:
    record = {
        "ts": "2026-05-27T10:00:00",
        "type": "wiki_query",
        "session_id": session_id,
        "filters": {"stage": stage, "type": "agent"},
        "hits": [],
        "hits_count": 0,
        "est_tokens_saved": 0,
    }
    with tmp_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def test_was_wiki_queried_true(tmp_log):
    _write_query(tmp_log, "sess1", "04")
    assert routing_log.was_wiki_queried("sess1", "04") is True


def test_was_wiki_queried_false_no_query(tmp_log):
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_false_wrong_stage(tmp_log):
    _write_query(tmp_log, "sess1", "03")
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_false_wrong_session(tmp_log):
    _write_query(tmp_log, "sess2", "04")
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_stage_prefix_match(tmp_log):
    # "04_brand" stage query should match was_wiki_queried("sess1", "04")
    _write_query(tmp_log, "sess1", "04_brand")
    assert routing_log.was_wiki_queried("sess1", "04") is True


def test_log_stage_start_via_wiki_true(tmp_log):
    _write_query(tmp_log, "sess1", "04")
    routing_log.log_stage_start("sess1", "04_brand", "lixiang-dubai3")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    stage_events = [e for e in events if e["type"] == "stage_start"]
    assert len(stage_events) == 1
    assert stage_events[0]["via_wiki"] is True
    assert stage_events[0]["stage"] == "04_brand"
    assert stage_events[0]["project"] == "lixiang-dubai3"


def test_log_stage_start_via_wiki_false(tmp_log):
    routing_log.log_stage_start("sess1", "04_brand", "lixiang-dubai3")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    stage_events = [e for e in events if e["type"] == "stage_start"]
    assert stage_events[0]["via_wiki"] is False


def test_log_agent_call_writes_record(tmp_log):
    _write_query(tmp_log, "sess1", "04")
    routing_log.log_agent_call("sess1", "brand-architect", "04")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    agent_events = [e for e in events if e["type"] == "agent_call"]
    assert len(agent_events) == 1
    assert agent_events[0]["agent"] == "brand-architect"
    assert agent_events[0]["via_wiki"] is True


def test_log_skill_call_writes_record(tmp_log):
    routing_log.log_skill_call("sess1", "landing-brand", "04")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    skill_events = [e for e in events if e["type"] == "skill_call"]
    assert len(skill_events) == 1
    assert skill_events[0]["skill"] == "landing-brand"
    assert skill_events[0]["via_wiki"] is False
```

- [ ] **Step 2: Запустить тесты — убедиться что падают**

```bash
cd d:/AI_TEAMS/landing_system
python -m pytest tests/wiki/test_launch_tracking.py -v 2>&1 | head -40
```

Ожидание: `AttributeError: module 'scripts.wiki.routing_log' has no attribute 'was_wiki_queried'`

- [ ] **Step 3: Добавить функции в `routing_log.py`**

В конец файла `scripts/wiki/routing_log.py` добавить:

```python
def was_wiki_queried(session_id: str, stage: str) -> bool:
    """True если в логе есть wiki_query с тем же session_id и совместимым stage."""
    if not LOG_PATH.exists():
        return False
    # Нормализуем stage: "04_brand" → "04", "04" → "04"
    stage_prefix = stage.split("_")[0] if "_" in stage else stage
    try:
        for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("type") != "wiki_query":
                continue
            if record.get("session_id") != session_id:
                continue
            f = record.get("filters") or {}
            rec_stage = str(f.get("stage") or "")
            rec_prefix = rec_stage.split("_")[0] if "_" in rec_stage else rec_stage
            if rec_prefix == stage_prefix or rec_stage == stage:
                return True
    except OSError:
        pass
    return False


def log_stage_start(session_id: str, stage: str, project: str) -> None:
    """Пишет stage_start с автоматической корреляцией via_wiki."""
    # Нормализуем номер из "04_brand" → "04"
    stage_prefix = stage.split("_")[0] if "_" in stage else stage
    via_wiki = was_wiki_queried(session_id, stage_prefix)
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "stage_start",
        "session_id": session_id,
        "stage": stage,
        "project": project,
        "via_wiki": via_wiki,
    })


def log_agent_call(session_id: str, agent: str, stage: str) -> None:
    """Пишет agent_call с автоматической корреляцией via_wiki."""
    via_wiki = was_wiki_queried(session_id, stage)
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "agent_call",
        "session_id": session_id,
        "agent": agent,
        "stage": stage,
        "via_wiki": via_wiki,
    })


def log_skill_call(session_id: str, skill: str, stage: str) -> None:
    """Пишет skill_call с автоматической корреляцией via_wiki."""
    via_wiki = was_wiki_queried(session_id, stage)
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "skill_call",
        "session_id": session_id,
        "skill": skill,
        "stage": stage,
        "via_wiki": via_wiki,
    })
```

- [ ] **Step 4: Запустить тесты — убедиться что проходят**

```bash
python -m pytest tests/wiki/test_launch_tracking.py -v
```

Ожидание: `10 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/routing_log.py tests/wiki/test_launch_tracking.py
git commit -m "feat(wiki-log): add was_wiki_queried + log_stage_start/agent_call/skill_call"
```

---

### Task 2: CLI `scripts/wiki/log.py`

**Files:**
- Create: `scripts/wiki/log.py`
- Test: `tests/wiki/test_launch_tracking.py` (добавить тест CLI)

- [ ] **Step 1: Добавить тест CLI**

В `tests/wiki/test_launch_tracking.py` добавить:

```python
import subprocess
import sys


def test_cli_log_agent_call(tmp_log, monkeypatch):
    # Прямой вызов через python -m scripts.wiki.log
    result = subprocess.run(
        [sys.executable, "-m", "scripts.wiki.log",
         "--type", "agent_call",
         "--agent", "brand-architect",
         "--stage", "04",
         "--session-id", "test-sess"],
        capture_output=True, text=True,
        cwd="d:/AI_TEAMS/landing_system"
    )
    assert result.returncode == 0
```

- [ ] **Step 2: Запустить — убедиться что падает**

```bash
python -m pytest tests/wiki/test_launch_tracking.py::test_cli_log_agent_call -v
```

Ожидание: `ModuleNotFoundError: No module named 'scripts.wiki.log'`

- [ ] **Step 3: Создать `scripts/wiki/log.py`**

```python
"""CLI для записи launch-событий в logs/wiki-usage.jsonl.

Использование:
    python -m scripts.wiki.log --type stage_start --stage 04_brand --project lixiang-dubai3
    python -m scripts.wiki.log --type agent_call --agent brand-architect --stage 04
    python -m scripts.wiki.log --type skill_call --skill landing-brand --stage 04

--session-id необязателен: берётся из $CLAUDE_SESSION_ID, иначе "unknown".
"""
from __future__ import annotations

import argparse
import os
import sys

from scripts.wiki import routing_log


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Log wiki launch event")
    p.add_argument("--type", required=True,
                   choices=["stage_start", "agent_call", "skill_call"])
    p.add_argument("--stage", default="")
    p.add_argument("--project", default="")
    p.add_argument("--agent", default="")
    p.add_argument("--skill", default="")
    p.add_argument("--session-id", default="")
    args = p.parse_args(argv[1:])

    session_id = args.session_id or os.environ.get("CLAUDE_SESSION_ID", "unknown")

    try:
        if args.type == "stage_start":
            routing_log.log_stage_start(session_id, args.stage, args.project)
        elif args.type == "agent_call":
            routing_log.log_agent_call(session_id, args.agent, args.stage)
        elif args.type == "skill_call":
            routing_log.log_skill_call(session_id, args.skill, args.stage)
    except Exception as e:
        print(f"[wiki log] failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Запустить тест — убедиться что проходит**

```bash
python -m pytest tests/wiki/test_launch_tracking.py -v
```

Ожидание: `11 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/log.py tests/wiki/test_launch_tracking.py
git commit -m "feat(wiki-log): add CLI scripts/wiki/log.py for launch event logging"
```

---

### Task 3: Интеграция в `gate-check.sh`

**Files:**
- Modify: `scripts/gate-check.sh`

- [ ] **Step 1: Добавить вызов log после определения переменных**

В `scripts/gate-check.sh` после строки `echo "═══ Gate check: stage=$stage project=..."` добавить:

```bash
# Log stage_start for wiki routing observability
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"
$PYTHON_CMD -m scripts.wiki.log \
    --type stage_start \
    --stage "$stage" \
    --project "$(basename "$project")" \
    --session-id "$SESSION_ID" \
    >/dev/null 2>&1 || true
```

- [ ] **Step 2: Проверить что gate-check не ломается при отсутствии лога**

```bash
bash scripts/gate-check.sh --stage 04_brand --project D:/AI_TEAMS/Lendings/lixiang-dubai3 2>&1 | head -5
```

Ожидание: команда продолжает работать нормально, без ошибок от wiki.log.

- [ ] **Step 3: Проверить что событие записалось**

```bash
python -c "
from scripts.wiki import routing_log
events = routing_log.read_events(since_days=1)
launches = [e for e in events if e.get('type') == 'stage_start']
print(f'stage_start events: {len(launches)}')
for e in launches[-3:]:
    print(e)
"
```

- [ ] **Step 4: Commit**

```bash
git add scripts/gate-check.sh
git commit -m "feat(wiki-log): log stage_start in gate-check.sh"
```

---

### Task 4: Интеграция в ключевые агенты

**Files:**
- Modify: `agents/landing-orchestrator.md`
- Modify: `agents/brand-architect.md`
- Modify: `agents/prototype-importer.md`
- Modify: `agents/references-curator.md`

- [ ] **Step 1: Найти pre-flight блок в каждом агенте**

```bash
grep -n "wiki.query\|Pre-flight\|pre-flight\|wiki log" agents/landing-orchestrator.md agents/brand-architect.md agents/prototype-importer.md agents/references-curator.md | head -20
```

- [ ] **Step 2: Добавить `wiki.log` в `landing-orchestrator.md`**

Найти строку с `python -m scripts.wiki.query --agent=landing-orchestrator` и после неё добавить:

```markdown
```bash
python -m scripts.wiki.log --type agent_call --agent landing-orchestrator --stage <current_stage>
```
```

Где `<current_stage>` берётся из текущего этапа pipeline (передаётся при вызове агента).

- [ ] **Step 3: Добавить в `brand-architect.md`**

После строки с `wiki.query --agent=brand-architect`:

```markdown
```bash
python -m scripts.wiki.log --type agent_call --agent brand-architect --stage 04
```
```

- [ ] **Step 4: Добавить в `prototype-importer.md`**

После строки с `wiki.query --agent=prototype-importer`:

```markdown
```bash
python -m scripts.wiki.log --type agent_call --agent prototype-importer --stage 07a
```
```

- [ ] **Step 5: Добавить в `references-curator.md`**

После строки с `wiki.query --agent=references-curator`:

```markdown
```bash
python -m scripts.wiki.log --type agent_call --agent references-curator --stage 03
```
```

- [ ] **Step 6: Commit**

```bash
git add agents/landing-orchestrator.md agents/brand-architect.md agents/prototype-importer.md agents/references-curator.md
git commit -m "feat(wiki-log): add agent_call logging to key agents pre-flight"
```

---

### Task 5: Секция "Запуски vs вики" в отчёте

**Files:**
- Modify: `scripts/wiki/stats.py`
- Test: `tests/wiki/test_launch_tracking.py` (добавить тесты отчёта)

- [ ] **Step 1: Добавить тесты отчёта**

В `tests/wiki/test_launch_tracking.py` добавить:

```python
from scripts.wiki import stats
from scripts.wiki.routing_log import log_stage_start, log_agent_call, log_skill_call


def test_stats_launches_section_in_report(tmp_log):
    # Записать wiki_query, затем agent_call
    _write_query(tmp_log, "sess1", "04")
    log_agent_call("sess1", "brand-architect", "04")
    log_skill_call("sess1", "landing-brand", "04")  # без prior query — утечка

    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    result = stats.compute_stats(events)
    report = stats.generate_report(result)

    assert "Запуски vs вики" in report
    assert "brand-architect" in report
    assert "landing-brand" in report


def test_stats_leak_marker_for_no_wiki(tmp_log):
    log_skill_call("sess1", "landing-brand", "04")  # без prior query

    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    result = stats.compute_stats(events)
    report = stats.generate_report(result)

    assert "⚠️" in report
```

- [ ] **Step 2: Запустить — убедиться что падают**

```bash
python -m pytest tests/wiki/test_launch_tracking.py::test_stats_launches_section_in_report tests/wiki/test_launch_tracking.py::test_stats_leak_marker_for_no_wiki -v
```

Ожидание: `AssertionError` (секции нет в отчёте)

- [ ] **Step 3: Расширить `StatsResult` в `stats.py`**

Добавить поле в датакласс:

```python
launches: list[dict] = field(default_factory=list)  # stage_start/agent_call/skill_call events
```

- [ ] **Step 4: Собирать launches в `compute_stats()`**

В цикл `for e in events:` добавить ветку:

```python
elif e.get("type") in ("stage_start", "agent_call", "skill_call"):
    result_launches.append(e)
```

И инициализировать `result_launches: list[dict] = []` перед циклом, присвоить `StatsResult.launches = result_launches` в конце.

- [ ] **Step 5: Добавить секцию в `generate_report()`**

После секции `### Детали wiki_query` добавить:

```python
if stats.launches:
    lines.append("\n## Запуски vs вики (7д)\n")
    lines.append("| Время | Тип | Имя | Stage | via_wiki | Утечка? |")
    lines.append("|-------|-----|-----|-------|----------|---------|")
    for e in stats.launches:
        ts = e.get("ts", "")[-8:-3]  # HH:MM
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
        lines.append(f"| {ts} | {tname} | {name} | {stage} | {via} | {leak} |")
```

- [ ] **Step 6: Запустить все тесты**

```bash
python -m pytest tests/wiki/ -v
```

Ожидание: все тесты проходят.

- [ ] **Step 7: Проверить отчёт вручную**

```bash
python -m scripts.wiki.stats --report && head -80 wiki/routing-report.md
```

- [ ] **Step 8: Commit**

```bash
git add scripts/wiki/stats.py tests/wiki/test_launch_tracking.py
git commit -m "feat(wiki-log): add Запуски vs вики section to routing report"
```

---

### Task 6: Финальная проверка

- [ ] **Step 1: Запустить полный тест-сьют wiki**

```bash
python -m pytest tests/wiki/ -v
```

Ожидание: все тесты зелёные.

- [ ] **Step 2: Проверить gate-check логирует stage_start**

```bash
bash scripts/gate-check.sh --stage 04_brand --project D:/AI_TEAMS/Lendings/lixiang-dubai3 2>&1 | head -10
python -c "
from scripts.wiki import routing_log
events = routing_log.read_events(since_days=1)
print([e for e in events if e.get('type') == 'stage_start'][-1])
"
```

- [ ] **Step 3: Проверить финальный отчёт**

```bash
python -m scripts.wiki.stats --report
cat wiki/routing-report.md
```

Ожидание: секция "Запуски vs вики" присутствует, `via_wiki` корректно показывает ✅/❌.

- [ ] **Step 4: Финальный commit**

```bash
git add -A
git commit -m "feat(wiki-log): complete stage/agent/skill launch tracking with via_wiki correlation"
```
