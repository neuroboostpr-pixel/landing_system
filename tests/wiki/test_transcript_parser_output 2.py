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
