import responses
from tools.api_validators import yandex_metrika


def test_missing_credentials(clean_env):
    r = yandex_metrika.validate()
    assert not r.is_valid


def test_missing_oauth_only(clean_env):
    clean_env.setenv("YM_COUNTER_ID", "12345678")
    r = yandex_metrika.validate()
    assert not r.is_valid


@responses.activate
def test_valid_credentials(clean_env):
    clean_env.setenv("YM_COUNTER_ID", "12345678")
    clean_env.setenv("YANDEX_METRIKA_OAUTH", "test-token")
    responses.add(responses.GET,
                  "https://api-metrika.yandex.net/management/v1/counter/12345678",
                  json={"counter": {}}, status=200)
    r = yandex_metrika.validate()
    assert r.is_valid


@responses.activate
def test_invalid_token(clean_env):
    clean_env.setenv("YM_COUNTER_ID", "12345678")
    clean_env.setenv("YANDEX_METRIKA_OAUTH", "bad")
    responses.add(responses.GET,
                  "https://api-metrika.yandex.net/management/v1/counter/12345678",
                  status=401)
    r = yandex_metrika.validate()
    assert not r.is_valid
