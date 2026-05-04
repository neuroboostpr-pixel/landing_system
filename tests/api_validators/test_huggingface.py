import responses
from tools.api_validators import huggingface

URL = "https://huggingface.co/api/whoami-v2"


def test_missing_key(clean_env):
    r = huggingface.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("HUGGINGFACE_TOKEN", "test-token")
    responses.add(responses.GET, URL, json={"name": "user"}, status=200)
    r = huggingface.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("HUGGINGFACE_TOKEN", "bad")
    responses.add(responses.GET, URL, status=401)
    r = huggingface.validate()
    assert not r.is_valid
