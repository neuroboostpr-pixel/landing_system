import responses
from tools.api_validators import telegram


def test_missing_credentials(clean_env):
    r = telegram.validate()
    assert not r.is_valid


@responses.activate
def test_valid_credentials(clean_env):
    clean_env.setenv("TG_BOT_TOKEN", "123:abc")
    clean_env.setenv("TG_CHAT_ID", "-1001234")
    responses.add(responses.GET, "https://api.telegram.org/bot123:abc/getMe",
                  json={"ok": True, "result": {"username": "bot"}}, status=200)
    responses.add(responses.GET, "https://api.telegram.org/bot123:abc/getChat",
                  json={"ok": True, "result": {"id": -1001234}}, status=200)
    r = telegram.validate()
    assert r.is_valid


@responses.activate
def test_invalid_bot_token(clean_env):
    clean_env.setenv("TG_BOT_TOKEN", "bad")
    clean_env.setenv("TG_CHAT_ID", "-1001234")
    responses.add(responses.GET, "https://api.telegram.org/botbad/getMe",
                  json={"ok": False}, status=401)
    r = telegram.validate()
    assert not r.is_valid
