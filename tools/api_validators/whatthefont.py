import os
import requests
from .base import ValidationResult

URL = "https://www.whatfontis.com/api/identify"


def validate() -> ValidationResult:
    key = os.getenv("WHATTHEFONT_API_KEY")
    if not key:
        return ValidationResult(False, "WHATTHEFONT_API_KEY not set in .env", "whatthefont")
    try:
        r = requests.post(URL, data={"API_KEY": key}, timeout=10)
        if r.status_code in (200, 400):
            return ValidationResult(True, "OK (auth accepted)", "whatthefont")
        return ValidationResult(False, f"HTTP {r.status_code}", "whatthefont")
    except Exception as e:
        return ValidationResult(False, str(e), "whatthefont")
