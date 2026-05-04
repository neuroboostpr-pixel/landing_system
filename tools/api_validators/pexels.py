import os
import requests
from .base import ValidationResult

URL = "https://api.pexels.com/v1/search"


def validate() -> ValidationResult:
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        return ValidationResult(False, "PEXELS_API_KEY not set in .env", "pexels")
    try:
        r = requests.get(URL, headers={"Authorization": key}, params={"query": "test", "per_page": 1}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "pexels")
        return ValidationResult(False, f"HTTP {r.status_code}", "pexels")
    except Exception as e:
        return ValidationResult(False, str(e), "pexels")
