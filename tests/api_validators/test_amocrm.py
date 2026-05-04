import responses
from tools.api_validators import amocrm


def test_missing(clean_env):
    r = amocrm.validate()
    assert not r.is_valid


@responses.activate
def test_valid(clean_env):
    clean_env.setenv("AMOCRM_API_KEY", "tok")
    clean_env.setenv("AMOCRM_SUBDOMAIN", "demo")
    responses.add(responses.GET, "https://demo.amocrm.ru/api/v4/account",
                  json={"id": 1, "name": "demo"}, status=200)
    r = amocrm.validate()
    assert r.is_valid


@responses.activate
def test_invalid(clean_env):
    clean_env.setenv("AMOCRM_API_KEY", "bad")
    clean_env.setenv("AMOCRM_SUBDOMAIN", "demo")
    responses.add(responses.GET, "https://demo.amocrm.ru/api/v4/account", status=401)
    r = amocrm.validate()
    assert not r.is_valid
