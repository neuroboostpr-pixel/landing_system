import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    counter = os.getenv("YM_COUNTER_ID")
    token = os.getenv("YANDEX_METRIKA_OAUTH")
    if not counter:
        return ValidationResult(False, "YM_COUNTER_ID not set", "yandex_metrika")
    if not token:
        return ValidationResult(False, "YANDEX_METRIKA_OAUTH not set", "yandex_metrika")
    try:
        r = requests.get(f"https://api-metrika.yandex.net/management/v1/counter/{counter}",
                         headers={"Authorization": f"OAuth {token}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "yandex_metrika")
        return ValidationResult(False, f"HTTP {r.status_code}", "yandex_metrika")
    except Exception as e:
        return ValidationResult(False, str(e), "yandex_metrika")
