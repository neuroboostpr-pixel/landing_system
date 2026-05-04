import responses
from tools.api_validators import regru

URL = "https://api.reg.ru/api/regru2/nop"


def test_missing(clean_env):
    r = regru.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("REGRU_API_USERNAME", "u")
    clean_env.setenv("REGRU_API_PASSWORD", "p")
    responses.add(responses.POST, URL, json={"result": "success"}, status=200)
    r = regru.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("REGRU_API_USERNAME", "u")
    clean_env.setenv("REGRU_API_PASSWORD", "bad")
    responses.add(responses.POST, URL, json={"result": "error", "error_text": "bad"}, status=200)
    r = regru.validate()
    assert not r.is_valid
