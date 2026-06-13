---
type: script
name: transcript_parser
language: python
sources: ["scripts/wiki/transcript_parser.py"]
updated: 2026-05-18
---

# transcript_parser.py

Парсит JSONL транскрипт Claude Code, извлекает tool calls.

ВНИМАНИЕ: самый хрупкий модуль — привязан к формату транскрипта Claude Code.
При обновлении Claude Code сначала смотреть tests/wiki/test_transcript_parser.py.

## Источник

- `scripts/wiki/transcript_parser.py`
