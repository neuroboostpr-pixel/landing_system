import responses
from tools.api_validators import pexels

URL = "https://api.pexels.com/v1/search?query=test&per_page=1"


def test_missing_key(clean_env):
    r = pexels.validate()
    assert not r.is_valid
    assert "PEXELS_API_KEY" in r.message


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("PEXELS_API_KEY", "test-key")
    responses.add(responses.GET, URL, json={"photos": []}, status=200)
    r = pexels.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("PEXELS_API_KEY", "bad")
    responses.add(responses.GET, URL, status=401)
    r = pexels.validate()
    assert not r.is_valid
