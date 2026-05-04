import responses
from tools.api_validators import yandex_wordstat

URL = "https://api.direct.yandex.com/json/v5/keywordsresearch"


def test_missing_token(clean_env):
    r = yandex_wordstat.validate()
    assert not r.is_valid


@responses.activate
def test_valid_token(clean_env):
    clean_env.setenv("YANDEX_OAUTH_TOKEN", "test-token")
    responses.add(responses.POST, URL, json={"result": {}}, status=200)
    r = yandex_wordstat.validate()
    assert r.is_valid


@responses.activate
def test_invalid_token(clean_env):
    clean_env.setenv("YANDEX_OAUTH_TOKEN", "bad")
    responses.add(responses.POST, URL, status=401)
    r = yandex_wordstat.validate()
    assert not r.is_valid
