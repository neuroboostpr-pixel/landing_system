import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    token = os.getenv("TG_BOT_TOKEN")
    chat = os.getenv("TG_CHAT_ID")
    if not token or not chat:
        return ValidationResult(False, "TG_BOT_TOKEN/TG_CHAT_ID not set", "telegram")
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if r.status_code != 200 or not r.json().get("ok"):
            return ValidationResult(False, f"getMe failed: HTTP {r.status_code}", "telegram")
        r2 = requests.get(f"https://api.telegram.org/bot{token}/getChat",
                          params={"chat_id": chat}, timeout=10)
        if r2.status_code != 200 or not r2.json().get("ok"):
            return ValidationResult(False, f"getChat failed: HTTP {r2.status_code}", "telegram")
        return ValidationResult(True, f"OK (bot @{r.json()['result'].get('username', '?')})", "telegram")
    except Exception as e:
        return ValidationResult(False, str(e), "telegram")
