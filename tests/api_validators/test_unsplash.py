import responses
from tools.api_validators import unsplash

URL = "https://api.unsplash.com/photos"


def test_missing_key(clean_env):
    r = unsplash.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("UNSPLASH_ACCESS_KEY", "test-key")
    responses.add(responses.GET, URL, json=[], status=200)
    r = unsplash.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("UNSPLASH_ACCESS_KEY", "bad")
    responses.add(responses.GET, URL, status=401)
    r = unsplash.validate()
    assert not r.is_valid
