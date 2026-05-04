import responses
from tools.api_validators import cloudflare

URL = "https://api.cloudflare.com/client/v4/user/tokens/verify"


def test_missing(clean_env):
    r = cloudflare.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("CLOUDFLARE_API_TOKEN", "tok")
    responses.add(responses.GET, URL, json={"success": True}, status=200)
    r = cloudflare.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("CLOUDFLARE_API_TOKEN", "bad")
    responses.add(responses.GET, URL, status=401)
    r = cloudflare.validate()
    assert not r.is_valid
