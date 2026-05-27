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
            try:
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except (ImportError, OSError):
                try:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                except (ImportError, OSError):
                    pass
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[wiki routing_log] failed to write: {e}", file=sys.stderr)


def log_query(
    session_id: str,
    filters: dict[str, str | None],
    hits: list[str],
    est_tokens_saved: int,
    model: str = "",
    thinking_tokens: int = 0,
    speed: str = "",
    entrypoint: str = "",
    is_sidechain: bool = False,
    agent: str = "",
) -> None:
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "wiki_query",
        "session_id": session_id,
        "model": model,
        "agent": agent,
        "thinking_tokens": thinking_tokens,
        "speed": speed,
        "entrypoint": entrypoint,
        "is_sidechain": is_sidechain,
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
    model: str = "",
    thinking_tokens: int = 0,
    speed: str = "",
    entrypoint: str = "",
    is_sidechain: bool = False,
) -> None:
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "direct_read",
        "session_id": session_id,
        "model": model,
        "thinking_tokens": thinking_tokens,
        "speed": speed,
        "entrypoint": entrypoint,
        "is_sidechain": is_sidechain,
        "path": path,
        "est_tokens": est_tokens,
        "had_prior_query": had_prior_query,
    })


def log_context_inject(
    session_id: str,
    source_category: str,
    source_label: str,
    est_tokens: int,
    can_be_wiki: bool = False,
    path: str = "",
    model: str = "",
) -> None:
    _write({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "type": "context_inject",
        "session_id": session_id,
        "model": model,
        "source_category": source_category,
        "source_label": source_label,
        "path": path,
        "est_tokens": est_tokens,
        "can_be_wiki": can_be_wiki,
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
    """Оценка токенов. Читает текст как UTF-8, считает символы / 3.5.
    Fallback: size / 4. Погрешность ~30% — достаточно для сравнения wiki vs source.
    """
    try:
        text = path.read_text(encoding="utf-8")
        return int(len(text) / 3.5)
    except (OSError, UnicodeDecodeError):
        try:
            return path.stat().st_size // 4
        except OSError:
            return 0


def _stage_prefix(stage: str) -> str:
    """Нормализует stage до числового префикса: '04_brand' → '04', '04' → '04'."""
    return stage.split("_")[0] if "_" in stage else stage


def was_wiki_queried(session_id: str, stage: str) -> bool:
    """True если в логе есть wiki_query с тем же session_id и совместимым stage."""
    if not stage:
        return False
    if not LOG_PATH.exists():
        return False
    stage_prefix = _stage_prefix(stage)
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
            rec_prefix = _stage_prefix(rec_stage)
            if rec_prefix == stage_prefix or rec_stage == stage:
                return True
    except OSError:
        pass
    return False


def log_stage_start(session_id: str, stage: str, project: str) -> None:
    """Пишет stage_start с автоматической корреляцией via_wiki."""
    via_wiki = was_wiki_queried(session_id, stage)  # was_wiki_queried сам нормализует
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
