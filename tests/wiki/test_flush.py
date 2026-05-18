"""Тесты flush.py с моком SDK."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.wiki import flush


FIXTURES = Path(__file__).parent / "fixtures" / "transcripts"


def test_read_transcript():
    """Читает JSONL и возвращает list[dict]."""
    msgs = flush.read_transcript(FIXTURES / "sample.jsonl")
    assert len(msgs) == 4
    assert msgs[0]["role"] == "user"


def test_format_transcript_for_sdk():
    """Превращает list[dict] в plain text для SDK."""
    msgs = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    text = flush.format_transcript(msgs)
    assert "user: hello" in text.lower()
    assert "assistant: hi" in text.lower()


def test_flush_writes_daily_log(tmp_path, mocker):
    """flush() извлекает уроки и аппендит в daily/YYYY-MM-DD.md."""
    mocker.patch(
        "scripts.wiki.flush.sdk_client.generate",
        return_value="- **[урок]** Тестовый урок",
    )
    memory_dir = tmp_path / "memory"
    flush.flush_transcript(
        transcript_path=FIXTURES / "sample.jsonl",
        memory_dir=memory_dir,
    )
    daily = memory_dir / "daily"
    assert daily.exists()
    files = list(daily.glob("*.md"))
    assert len(files) == 1
    assert "Тестовый урок" in files[0].read_text(encoding="utf-8")


def test_flush_skips_empty_result(tmp_path, mocker):
    """Если SDK вернул '_(пусто)_' — daily не создаётся."""
    mocker.patch(
        "scripts.wiki.flush.sdk_client.generate",
        return_value="_(пусто)_",
    )
    memory_dir = tmp_path / "memory"
    flush.flush_transcript(
        transcript_path=FIXTURES / "sample.jsonl",
        memory_dir=memory_dir,
    )
    daily = memory_dir / "daily"
    # Папка может быть создана, но без файлов
    if daily.exists():
        assert list(daily.glob("*.md")) == []
