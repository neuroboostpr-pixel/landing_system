import os
import subprocess
from .base import ValidationResult


def validate() -> ValidationResult:
    user = os.getenv("BEGET_USER")
    host = os.getenv("BEGET_HOST")
    if not user or not host:
        return ValidationResult(False, "BEGET_USER/BEGET_HOST not set", "beget_ssh")
    try:
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
             f"{user}@{host}", "echo ok"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and "ok" in r.stdout:
            return ValidationResult(True, "OK", "beget_ssh")
        return ValidationResult(False, f"exit {r.returncode}: {r.stderr[:120]}", "beget_ssh")
    except Exception as e:
        return ValidationResult(False, str(e), "beget_ssh")
