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
    names = {tc.tool_name for tc in tcs}
    assert "Read" in names


def test_missing_input_field_skipped():
    from scripts.wiki.transcript_parser import extract_tool_calls
    tcs = extract_tool_calls(FIXTURES / "broken.jsonl")
    bashes = [tc for tc in tcs if tc.tool_name == "Bash"]
    assert all("command" in tc.input_params or tc.input_params == {} for tc in bashes)


def test_broken_json_line_skipped():
    from scripts.wiki.transcript_parser import extract_tool_calls
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


def test_extracts_model_from_message():
    from scripts.wiki.transcript_parser import extract_tool_calls
    tcs = extract_tool_calls(FIXTURES / "normal.jsonl")
    assert all(isinstance(tc.model, str) for tc in tcs)


def test_extracts_thinking_tokens(tmp_path):
    from scripts.wiki.transcript_parser import extract_tool_calls
    transcript = tmp_path / "thinking.jsonl"
    import json
    record = {
        "parentUuid": None,
        "sessionId": "test-thinking",
        "message": {
            "model": "claude-opus-4-7",
            "role": "assistant",
            "content": [
                {"type": "thinking", "thinking": "x" * 350},
                {"type": "tool_use", "name": "Read", "input": {"file_path": "/path/agents/wp-builder.md"}},
            ]
        },
        "type": "assistant",
        "uuid": "uuid-t1",
        "timestamp": "2026-05-27T10:00:01.000Z"
    }
    transcript.write_text(json.dumps(record) + "\n", encoding="utf-8")
    tcs = extract_tool_calls(transcript)
    assert len(tcs) == 1
    assert tcs[0].model == "claude-opus-4-7"
    assert tcs[0].thinking_tokens == int(350 / 3.5)  # 100


def test_extracts_speed_and_entrypoint(tmp_path):
    from scripts.wiki.transcript_parser import extract_tool_calls
    transcript = tmp_path / "speed.jsonl"
    import json
    record = {
        "parentUuid": None,
        "sessionId": "test-speed",
        "isSidechain": True,
        "entrypoint": "claude-cli",
        "message": {
            "model": "claude-opus-4-7",
            "role": "assistant",
            "usage": {"speed": "fast", "input_tokens": 100, "output_tokens": 50},
            "content": [
                {"type": "tool_use", "name": "Bash",
                 "input": {"command": "python -m scripts.wiki.query --stage=08"}}
            ]
        },
        "type": "assistant",
        "uuid": "uuid-sp1",
        "timestamp": "2026-05-27T10:00:01.000Z"
    }
    transcript.write_text(json.dumps(record) + "\n", encoding="utf-8")
    tcs = extract_tool_calls(transcript)
    assert len(tcs) == 1
    assert tcs[0].speed == "fast"
    assert tcs[0].entrypoint == "claude-cli"
    assert tcs[0].is_sidechain is True


def test_source_read_uses_config_patterns(monkeypatch):
    """При изменении SOURCE_READ_PATTERNS — is_source_read отражает новый конфиг."""
    from scripts.wiki import config as wiki_config
    from scripts.wiki.transcript_parser import ToolCall, is_source_read

    monkeypatch.setattr(wiki_config, "SOURCE_READ_PATTERNS", ["custom/*.md"])
    tc_custom = ToolCall(ts="", tool_name="Read", input_params={"file_path": "/root/custom/foo.md"})
    tc_agent = ToolCall(ts="", tool_name="Read", input_params={"file_path": "/root/agents/bar.md"})

    assert is_source_read(tc_custom) is True
    assert is_source_read(tc_agent) is False
