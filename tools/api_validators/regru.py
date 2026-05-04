import os
import requests
from .base import ValidationResult

URL = "https://api.reg.ru/api/regru2/nop"


def validate() -> ValidationResult:
    user = os.getenv("REGRU_API_USERNAME")
    pwd = os.getenv("REGRU_API_PASSWORD")
    if not user or not pwd:
        return ValidationResult(False, "REGRU_API_USERNAME/PASSWORD not set", "regru")
    try:
        r = requests.post(URL, data={"username": user, "password": pwd, "output_format": "json"}, timeout=10)
        if r.status_code == 200 and r.json().get("result") == "success":
            return ValidationResult(True, "OK", "regru")
        return ValidationResult(False, f"{r.json().get('error_text', f'HTTP {r.status_code}')}", "regru")
    except Exception as e:
        return ValidationResult(False, str(e), "regru")
