import os
import requests
from .base import ValidationResult

URL = "https://huggingface.co/api/whoami-v2"


def validate() -> ValidationResult:
    key = os.getenv("HUGGINGFACE_TOKEN")
    if not key:
        return ValidationResult(False, "HUGGINGFACE_TOKEN not set in .env", "huggingface")
    try:
        r = requests.get(URL, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, f"OK (user: {r.json().get('name', '?')})", "huggingface")
        return ValidationResult(False, f"HTTP {r.status_code}", "huggingface")
    except Exception as e:
        return ValidationResult(False, str(e), "huggingface")
