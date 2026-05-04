import os
import requests
from .base import ValidationResult


def validate() -> ValidationResult:
    key = os.getenv("AMOCRM_API_KEY")
    sub = os.getenv("AMOCRM_SUBDOMAIN")
    if not key or not sub:
        return ValidationResult(False, "AMOCRM_API_KEY/SUBDOMAIN not set", "amocrm")
    try:
        r = requests.get(f"https://{sub}.amocrm.ru/api/v4/account",
                         headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            return ValidationResult(True, "OK", "amocrm")
        return ValidationResult(False, f"HTTP {r.status_code}", "amocrm")
    except Exception as e:
        return ValidationResult(False, str(e), "amocrm")
