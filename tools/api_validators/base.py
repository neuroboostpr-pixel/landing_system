from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    message: str
    service: str

    def __bool__(self) -> bool:
        return self.is_valid

    def __str__(self) -> str:
        prefix = "✅" if self.is_valid else "❌"
        return f"{prefix} {self.service}: {self.message}"
