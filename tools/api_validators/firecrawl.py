import os
import requests
from .base import ValidationResult

URL = "https://api.firecrawl.dev/v0/credits"


def validate() -> ValidationResult:
    key = os.getenv("FIRECRAWL_API_KEY")
    if not key:
        return ValidationResult(False, "FIRECRAWL_API_KEY not set in .env", "firecrawl")
    try:
        r = requests.get(URL, headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, f"OK ({r.json().get('credits', '?')} credits)", "firecrawl")
        return ValidationResult(False, f"HTTP {r.status_code}: {r.text[:120]}", "firecrawl")
    except Exception as e:
        return ValidationResult(False, str(e), "firecrawl")
