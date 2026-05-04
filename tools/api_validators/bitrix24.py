import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    url = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/")
    if not url:
        return ValidationResult(False, "BITRIX24_WEBHOOK_URL not set", "bitrix24")
    try:
        r = requests.get(f"{url}/profile.json", timeout=10)
        if r.status_code == 200 and r.json().get("result"):
            return ValidationResult(True, "OK", "bitrix24")
        return ValidationResult(False, f"HTTP {r.status_code}", "bitrix24")
    except Exception as e:
        return ValidationResult(False, str(e), "bitrix24")
