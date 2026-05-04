import pytest


@pytest.fixture
def clean_env(monkeypatch):
    """Removes all API-related env vars before test."""
    keys = [
        "FIRECRAWL_API_KEY", "PEXELS_API_KEY", "UNSPLASH_ACCESS_KEY",
        "PIXABAY_API_KEY", "HUGGINGFACE_TOKEN", "WHATTHEFONT_API_KEY",
        "YANDEX_OAUTH_TOKEN", "YANDEX_METRIKA_OAUTH", "YM_COUNTER_ID",
        "TG_BOT_TOKEN", "TG_CHAT_ID", "AMOCRM_API_KEY", "AMOCRM_SUBDOMAIN",
        "BITRIX24_WEBHOOK_URL", "BEGET_USER", "BEGET_HOST",
        "BEGET_API_LOGIN", "BEGET_API_PASSWORD",
        "CLOUDFLARE_API_TOKEN", "REGRU_API_USERNAME", "REGRU_API_PASSWORD",
    ]
    for k in keys:
        monkeypatch.delenv(k, raising=False)
    return monkeypatch
