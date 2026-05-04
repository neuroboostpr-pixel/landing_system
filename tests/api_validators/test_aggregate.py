from unittest.mock import patch
from tools.api_validators.aggregate import run_all
from tools.api_validators.base import ValidationResult


def test_run_all_collects_all_services():
    with patch("tools.api_validators.firecrawl.validate", return_value=ValidationResult(True, "OK", "firecrawl")), \
         patch("tools.api_validators.pexels.validate", return_value=ValidationResult(False, "x", "pexels")):
        results = run_all(only=["firecrawl", "pexels"])
        assert len(results) == 2
        assert results[0].service == "firecrawl"
        assert results[0].is_valid
        assert not results[1].is_valid


def test_run_all_default_runs_all_15():
    results = run_all()
    services = {r.service for r in results}
    expected = {"firecrawl", "pexels", "unsplash", "pixabay", "huggingface",
                "whatthefont", "yandex_wordstat", "yandex_metrika", "telegram",
                "amocrm", "bitrix24", "beget_ssh", "beget_api", "cloudflare", "regru"}
    assert services == expected
