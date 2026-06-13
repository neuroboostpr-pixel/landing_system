"""Preflight checks для wiki routing системы.

Вызывается из session_start.py перед логированием.
При failures — блокирует запуск и предлагает fix_hint.
Переопределить через WIKI_PREFLIGHT_SKIP=1.
"""
from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.wiki import config


@dataclass
class CheckResult:
    ok: bool
    name: str
    message: str
    fix_hint: str


def check_disk_space(min_mb: int = 50) -> CheckResult:
    try:
        usage = shutil.disk_usage(config.REPO_ROOT)
        free_mb = usage.free // (1024 * 1024)
        if free_mb < min_mb:
            return CheckResult(
                ok=False,
                name="disk_space",
                message=f"Less than {min_mb}MB free ({free_mb}MB available)",
                fix_hint="Free up disk space",
            )
        return CheckResult(ok=True, name="disk_space", message=f"{free_mb}MB free", fix_hint="")
    except OSError as e:
        return CheckResult(ok=False, name="disk_space", message=str(e), fix_hint="Check disk")


def check_logs_dir_writable() -> CheckResult:
    from scripts.wiki import routing_log
    logs_dir = routing_log.LOG_PATH.parent
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        test_file = logs_dir / ".preflight_write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        return CheckResult(ok=True, name="logs_writable", message=str(logs_dir), fix_hint="")
    except OSError as e:
        return CheckResult(
            ok=False,
            name="logs_writable",
            message=f"logs/ not writable: {logs_dir} ({e})",
            fix_hint=f"mkdir {logs_dir} && check permissions",
        )


def check_index_yaml_exists() -> CheckResult:
    index = config.WIKI_DIR / "index.yaml"
    if index.exists():
        return CheckResult(ok=True, name="index_exists", message=str(index), fix_hint="")
    return CheckResult(
        ok=False,
        name="index_exists",
        message="index.yaml missing",
        fix_hint="python -m scripts.wiki.compile --source-mode=system",
    )


def check_index_yaml_parseable() -> CheckResult:
    index = config.WIKI_DIR / "index.yaml"
    if not index.exists():
        return CheckResult(
            ok=False,
            name="index_parseable",
            message="index.yaml missing (cannot parse)",
            fix_hint="python -m scripts.wiki.compile --source-mode=system",
        )
    try:
        import yaml
        data = yaml.safe_load(index.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "concepts" not in data:
            raise ValueError("missing 'concepts' key")
        return CheckResult(ok=True, name="index_parseable", message="ok", fix_hint="")
    except Exception as e:
        return CheckResult(
            ok=False,
            name="index_parseable",
            message=f"index.yaml parse error: {e}",
            fix_hint="python -m scripts.wiki.compile --source-mode=system",
        )


def run_preflight() -> list[CheckResult]:
    """Runs all checks. Never raises exceptions."""
    checks = [
        check_disk_space,
        check_logs_dir_writable,
        check_index_yaml_exists,
        check_index_yaml_parseable,
    ]
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            results.append(CheckResult(
                ok=False,
                name=check.__name__,
                message=f"Unexpected error: {e}",
                fix_hint="Check logs",
            ))
    return results
