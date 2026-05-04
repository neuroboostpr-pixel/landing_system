import responses
from tools.api_validators import beget_api

URL = "https://api.beget.com/api/user/getAccountInfo"


def test_missing(clean_env):
    r = beget_api.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("BEGET_API_LOGIN", "u")
    clean_env.setenv("BEGET_API_PASSWORD", "p")
    responses.add(responses.GET, URL, json={"status": "success"}, status=200)
    r = beget_api.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("BEGET_API_LOGIN", "u")
    clean_env.setenv("BEGET_API_PASSWORD", "bad")
    responses.add(responses.GET, URL, json={"status": "error", "error_text": "bad creds"}, status=200)
    r = beget_api.validate()
    assert not r.is_valid
