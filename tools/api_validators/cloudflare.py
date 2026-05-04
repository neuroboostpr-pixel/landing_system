import os
import requests
from .base import ValidationResult

URL = "https://api.cloudflare.com/client/v4/user/tokens/verify"


def validate() -> ValidationResult:
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not token:
        return ValidationResult(False, "CLOUDFLARE_API_TOKEN not set", "cloudflare")
    try:
        r = requests.get(URL, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        if r.status_code == 200 and r.json().get("success"):
            return ValidationResult(True, "OK", "cloudflare")
        return ValidationResult(False, f"HTTP {r.status_code}", "cloudflare")
    except Exception as e:
        return ValidationResult(False, str(e), "cloudflare")
