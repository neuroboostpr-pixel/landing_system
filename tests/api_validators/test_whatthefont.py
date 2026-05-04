import responses
from tools.api_validators import whatthefont

URL = "https://www.whatfontis.com/api/identify"


def test_missing_key(clean_env):
    r = whatthefont.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("WHATTHEFONT_API_KEY", "test-key")
    responses.add(responses.POST, URL, json={"error": "missing image"}, status=400)
    r = whatthefont.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("WHATTHEFONT_API_KEY", "bad")
    responses.add(responses.POST, URL, status=401)
    r = whatthefont.validate()
    assert not r.is_valid
