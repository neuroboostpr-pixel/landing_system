import responses
from tools.api_validators import pixabay


def test_missing_key(clean_env):
    r = pixabay.validate()
    assert not r.is_valid


@responses.activate
def test_valid_key(clean_env):
    clean_env.setenv("PIXABAY_API_KEY", "test-key")
    responses.add(responses.GET, "https://pixabay.com/api/", json={"hits": []}, status=200)
    r = pixabay.validate()
    assert r.is_valid


@responses.activate
def test_invalid_key(clean_env):
    clean_env.setenv("PIXABAY_API_KEY", "bad")
    responses.add(responses.GET, "https://pixabay.com/api/", status=400)
    r = pixabay.validate()
    assert not r.is_valid
