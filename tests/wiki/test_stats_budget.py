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
