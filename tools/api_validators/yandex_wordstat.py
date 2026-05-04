import os
import requests
from .base import ValidationResult

URL = "https://api.direct.yandex.com/json/v5/keywordsresearch"


def validate() -> ValidationResult:
    token = os.getenv("YANDEX_OAUTH_TOKEN")
    if not token:
        return ValidationResult(False, "YANDEX_OAUTH_TOKEN not set in .env", "yandex_wordstat")
    try:
        r = requests.post(URL, headers={"Authorization": f"Bearer {token}"},
                          json={"method": "get", "params": {"Keywords": ["test"]}}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "yandex_wordstat")
        return ValidationResult(False, f"HTTP {r.status_code}", "yandex_wordstat")
    except Exception as e:
        return ValidationResult(False, str(e), "yandex_wordstat")
