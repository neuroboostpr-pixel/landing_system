import responses
from tools.api_validators import bitrix24


def test_missing(clean_env):
    r = bitrix24.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("BITRIX24_WEBHOOK_URL", "https://demo.bitrix24.ru/rest/1/abc")
    responses.add(responses.GET, "https://demo.bitrix24.ru/rest/1/abc/profile.json",
                  json={"result": {"ID": 1}}, status=200)
    r = bitrix24.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("BITRIX24_WEBHOOK_URL", "https://demo.bitrix24.ru/rest/1/bad")
    responses.add(responses.GET, "https://demo.bitrix24.ru/rest/1/bad/profile.json", status=401)
    r = bitrix24.validate()
    assert not r.is_valid
