import responses
from tools.api_validators import firecrawl

URL = "https://api.firecrawl.dev/v0/credits"


def test_missing_key(clean_env):
    r = firecrawl.validate()
    assert not r.is_valid
    assert "FIRECRAWL_API_KEY" in r.message


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("FIRECRAWL_API_KEY", "test-key")
    responses.add(responses.GET, URL, json={"credits": 500}, status=200)
    r = firecrawl.validate()
    assert r.is_valid
    assert r.service == "firecrawl"


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("FIRECRAWL_API_KEY", "bad")
    responses.add(responses.GET, URL, status=401)
    r = firecrawl.validate()
    assert not r.is_valid
    assert "401" in r.message
