---
type: script
name: sdk_client
language: python
sources: ["scripts/wiki/sdk_client.py"]
updated: 2026-05-18
---

# sdk_client.py

Обёртка над claude-agent-sdk.

В юнит-тестах функция ``_sdk_query()`` мокается. В production вызывает
реальный SDK через ``claude_agent_sdk.query`` (async API 0.2.x).

Авторизация — через подписку Claude Code (~/.claude/auth.json),
ANTHROPIC_API_KEY не требуется.

Модель по умолчанию — ``sonnet`` (быстрее и дешевле опуса для
компиляции wiki-концептов).

## Источник

- `scripts/wiki/sdk_client.py`
