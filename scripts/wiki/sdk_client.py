"""Обёртка над claude-agent-sdk.

В юнит-тестах функция ``_sdk_query()`` мокается. В production вызывает
реальный SDK через ``claude_agent_sdk.query`` (async API 0.2.x).

Авторизация — через подписку Claude Code (~/.claude/auth.json),
ANTHROPIC_API_KEY не требуется.

Модель по умолчанию — ``sonnet`` (быстрее и дешевле опуса для
компиляции wiki-концептов).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass


class SDKError(RuntimeError):
    """Ошибка вызова SDK или пустой ответ."""


@dataclass
class SDKResponse:
    content: str


# Дефолтная модель для wiki-компиляции.
DEFAULT_MODEL = "sonnet"


def _sdk_query(system: str, user: str) -> SDKResponse:
    """Реальный вызов claude-agent-sdk. Заменяется моком в тестах.

    Использует асинхронный ``query()`` SDK 0.2.x: собирает все
    AssistantMessage из стрима и склеивает текстовые блоки в один
    string. Системный промпт уходит в ``ClaudeAgentOptions.system_prompt``,
    user-сообщение — в ``prompt``.
    """
    # Импорт внутри — чтобы тесты не падали при отсутствии SDK в окружении
    # и чтобы импорт sdk_client был дешёвым.
    from claude_agent_sdk import (  # type: ignore
        AssistantMessage,
        ClaudeAgentOptions,
        TextBlock,
        query,
    )

    async def _run() -> str:
        options = ClaudeAgentOptions(
            system_prompt=system,
            model=DEFAULT_MODEL,
            permission_mode="bypassPermissions",
            max_turns=50,
        )
        chunks: list[str] = []
        async for message in query(prompt=user, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
        return "".join(chunks)

    text = asyncio.run(_run())
    return SDKResponse(content=text)


def generate(system: str, user: str) -> str:
    """Вызывает SDK и возвращает очищенный ответ.

    Raises:
        SDKError: если SDK вернул пустую строку или упал с ошибкой
            (включая ``Claude Code returned an error result: ...`` от
            claude_agent_sdk при is_error=True + ненулевом exit).
    """
    try:
        response = _sdk_query(system=system, user=user)
    except SDKError:
        raise
    except Exception as e:
        raise SDKError(f"SDK call failed: {e}") from e
    content = (response.content or "").strip()
    if not content:
        raise SDKError("SDK вернул пустой content")
    return content
