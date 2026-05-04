import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return ValidationResult(False, "PIXABAY_API_KEY not set in .env", "pixabay")
    try:
        r = requests.get("https://pixabay.com/api/", params={"key": key, "per_page": 3}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "pixabay")
        return ValidationResult(False, f"HTTP {r.status_code}", "pixabay")
    except Exception as e:
        return ValidationResult(False, str(e), "pixabay")
