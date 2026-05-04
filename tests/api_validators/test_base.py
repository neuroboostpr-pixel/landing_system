from tools.api_validators.base import ValidationResult


def test_validation_result_is_dataclass():
    r = ValidationResult(is_valid=True, message="ok", service="x")
    assert r.is_valid is True
    assert r.message == "ok"
    assert r.service == "x"


def test_validation_result_bool():
    assert bool(ValidationResult(True, "ok", "x")) is True
    assert bool(ValidationResult(False, "fail", "x")) is False


def test_validation_result_str():
    r = ValidationResult(True, "OK", "firecrawl")
    assert "firecrawl" in str(r)
    assert "OK" in str(r)
