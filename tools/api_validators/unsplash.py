import os
import requests
from .base import ValidationResult

URL = "https://api.unsplash.com/photos"


def validate() -> ValidationResult:
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not key:
        return ValidationResult(False, "UNSPLASH_ACCESS_KEY not set in .env", "unsplash")
    try:
        r = requests.get(URL, headers={"Authorization": f"Client-ID {key}"}, params={"per_page": 1}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "unsplash")
        return ValidationResult(False, f"HTTP {r.status_code}", "unsplash")
    except Exception as e:
        return ValidationResult(False, str(e), "unsplash")
