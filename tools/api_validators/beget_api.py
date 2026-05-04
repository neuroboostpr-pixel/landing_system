import os
import requests
from .base import ValidationResult

URL = "https://api.beget.com/api/user/getAccountInfo"


def validate() -> ValidationResult:
    login = os.getenv("BEGET_API_LOGIN")
    pwd = os.getenv("BEGET_API_PASSWORD")
    if not login or not pwd:
        return ValidationResult(False, "BEGET_API_LOGIN/PASSWORD not set", "beget_api")
    try:
        r = requests.get(URL, params={"login": login, "passwd": pwd, "input_format": "json", "output_format": "json"}, timeout=10)
        if r.status_code == 200 and r.json().get("status") == "success":
            return ValidationResult(True, "OK", "beget_api")
        return ValidationResult(False, f"{r.json().get('error_text', f'HTTP {r.status_code}')}", "beget_api")
    except Exception as e:
        return ValidationResult(False, str(e), "beget_api")
