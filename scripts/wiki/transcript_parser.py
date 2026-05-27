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
    session_id: str = ""
    model: str = ""
    thinking_tokens: int = 0
    speed: str = ""
    entrypoint: str = ""
    is_sidechain: bool = False


def extract_tool_calls(transcript_path: Path) -> list[ToolCall]:
    """Reads Claude Code JSONL transcript, returns all tool calls.

    Real format (investigated 2026-05-27):
      {"parentUuid": "...", "sessionId": "...", "message": {"role": "assistant",
       "content": [{"type": "tool_use", "name": "Read", "input": {...}}]},
       "timestamp": "...", "uuid": "..."}

    Skips broken lines silently.
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
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        msg = obj.get("message")
        if not isinstance(msg, dict):
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue

        ts = obj.get("timestamp", "")
        session_id = obj.get("sessionId", "")
        model = msg.get("model", "")
        speed = (msg.get("usage") or {}).get("speed", "")
        entrypoint = obj.get("entrypoint", "")
        is_sidechain = bool(obj.get("isSidechain", False))

        thinking_tokens = 0
        for block in content:
            if isinstance(block, dict) and block.get("type") == "thinking":
                thinking_tokens += int(len(block.get("thinking", "")) / 3.5)

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
            result.append(ToolCall(
                ts=ts, tool_name=name, input_params=input_params,
                session_id=session_id, model=model, thinking_tokens=thinking_tokens,
                speed=speed, entrypoint=entrypoint, is_sidechain=is_sidechain,
            ))

    return result


def is_source_read(tc: ToolCall) -> bool:
    """True if Read tool with path matching SOURCE_READ_PATTERNS (not a wiki card)."""
    if tc.tool_name != "Read":
        return False
    path = tc.input_params.get("file_path", "")
    if "wiki/concepts/" in path or "wiki\\concepts\\" in path:
        return False
    return _matches_source_patterns(path)


def _matches_source_patterns(path: str) -> bool:
    import fnmatch
    for pattern in config.SOURCE_READ_PATTERNS:
        norm_path = path.replace("\\", "/")
        if fnmatch.fnmatch(norm_path, f"*/{pattern}") or fnmatch.fnmatch(norm_path, pattern):
            return True
    return False


def is_wiki_query(tc: ToolCall) -> bool:
    """True if Bash tool with 'scripts.wiki.query' in command."""
    if tc.tool_name != "Bash":
        return False
    command = tc.input_params.get("command", "")
    return "scripts.wiki.query" in command


def get_session_id(transcript_path: Path) -> str:
    """Reads sessionId from first record. Fallback: filename stem."""
    try:
        for line in transcript_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            sid = obj.get("sessionId")
            if sid:
                return sid
    except (OSError, json.JSONDecodeError):
        pass
    return transcript_path.stem


def extract_query_slugs(tc: ToolCall) -> list[str]:
    """Extracts --slug= values from Bash wiki query command."""
    command = tc.input_params.get("command", "")
    return re.findall(r"--slug[= ](\S+)", command)


def extract_query_stage(tc: ToolCall) -> str | None:
    """Extracts --stage= value from Bash wiki query command."""
    command = tc.input_params.get("command", "")
    m = re.search(r"--stage[= ](\S+)", command)
    return m.group(1) if m else None
