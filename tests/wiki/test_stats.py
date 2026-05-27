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
