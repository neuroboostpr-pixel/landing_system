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
    output: str = ""


def extract_tool_calls(transcript_path: Path) -> list[ToolCall]:
    """Reads Claude Code JSONL transcript, returns all tool calls with outputs.

    Real format (investigated 2026-05-27):
      {"parentUuid": "...", "sessionId": "...", "message": {"role": "assistant",
       "content": [{"type": "tool_use", "id": "...", "name": "Read", "input": {...}}]},
       "timestamp": "...", "uuid": "..."}
      {"parentUuid": "...", "sessionId": "...", "message": {"role": "user",
       "content": [{"type": "tool_result", "tool_use_id": "...", "content": [...]}]},
       "timestamp": "...", "uuid": "..."}

    Matches toolResult records to toolUse by tool_use_id.
    Skips broken lines silently.
    """
    calls: list[ToolCall] = []
    tool_ids: list[str] = []
    records: list[dict] = []

    try:
        text = transcript_path.read_text(encoding="utf-8")
    except OSError:
        return calls

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    for record in records:
        msg = record.get("message")
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "assistant":
            continue

        content = msg.get("content")
        if not isinstance(content, list):
            continue

        ts = record.get("timestamp", "")
        session_id = record.get("sessionId", "")
        model = msg.get("model", "")
        speed = (msg.get("usage") or {}).get("speed", "")
        entrypoint = record.get("entrypoint", "")
        is_sidechain = bool(record.get("isSidechain", False))

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
            tool_id = block.get("id", "")
            calls.append(ToolCall(
                ts=ts, tool_name=name, input_params=input_params,
                session_id=session_id, model=model, thinking_tokens=thinking_tokens,
                speed=speed, entrypoint=entrypoint, is_sidechain=is_sidechain,
                output="",
            ))
            tool_ids.append(tool_id)

    # Second pass: match toolResult → tool output by tool_use_id
    result_map: dict[str, str] = {}
    for record in records:
        msg = record.get("message")
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "user":
            continue
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_result":
                continue
            tool_use_id = block.get("tool_use_id", "")
            if not tool_use_id:
                continue
            content_block = block.get("content", "")
            if isinstance(content_block, str):
                result_map[tool_use_id] = content_block
            elif isinstance(content_block, list):
                parts = [
                    b.get("text", "") for b in content_block
                    if isinstance(b, dict) and b.get("type") == "text"
                ]
                result_map[tool_use_id] = "\n".join(parts)

    for call, tool_id in zip(calls, tool_ids):
        call.output = result_map.get(tool_id, "")

    return calls


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
