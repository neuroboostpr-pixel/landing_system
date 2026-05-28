"""Tests for scripts/wiki/stats.py."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest


def _make_events(n_queries=3, n_reads=2, bypass_prior=1):
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
    assert "запросов к вики" in line
    assert "обходов вики" in line
    assert "токенов сэкономлено" in line
    assert "доля обходов" in line


def test_generate_report_markdown():
    from scripts.wiki.stats import compute_stats, generate_report
    events = _make_events(n_queries=5, n_reads=2)
    result = compute_stats(events)
    md = generate_report(result)
    assert "# Отчёт по использованию вики-графа" in md
    assert "Топ файлов читаемых в обход" in md
    assert "had_prior_query_count" not in md  # stored in StatsResult, not rendered raw


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
