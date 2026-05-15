"""Тесты sdk_client (с моком claude_agent_sdk)."""
from unittest.mock import MagicMock, patch

import pytest

from scripts.wiki import sdk_client


def test_generate_calls_sdk(mocker):
    """generate() вызывает SDK с собранным промптом."""
    fake_response = MagicMock()
    fake_response.content = "compiled article body"
    mock_query = mocker.patch.object(
        sdk_client, "_sdk_query", return_value=fake_response
    )

    result = sdk_client.generate(
        system="You compile wiki articles.",
        user="Source: agent foo\n\nContent: bar",
    )

    assert result == "compiled article body"
    mock_query.assert_called_once()
    call_kwargs = mock_query.call_args.kwargs
    assert "system" in call_kwargs
    assert "user" in call_kwargs


def test_generate_empty_response_raises(mocker):
    """Если SDK вернул пустой content — кидаем."""
    fake_response = MagicMock()
    fake_response.content = ""
    mocker.patch.object(sdk_client, "_sdk_query", return_value=fake_response)

    with pytest.raises(sdk_client.SDKError):
        sdk_client.generate(system="s", user="u")


def test_generate_strips_response(mocker):
    """Ведущие/завершающие пробелы в ответе SDK обрезаются."""
    fake_response = MagicMock()
    fake_response.content = "  \n\nbody\n\n  "
    mocker.patch.object(sdk_client, "_sdk_query", return_value=fake_response)
    assert sdk_client.generate(system="s", user="u") == "body"
