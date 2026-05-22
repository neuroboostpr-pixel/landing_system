"""Integration test: run-audit.py CLI end-to-end."""
import json
import subprocess
import sys
from pathlib import Path
import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
RUN_AUDIT = SKILL_ROOT / "scripts" / "run-audit.py"
FIXTURES = SKILL_ROOT / "tests" / "fixtures"


def test_cli_help():
    r = subprocess.run([sys.executable, str(RUN_AUDIT), "--help"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "--project" in r.stdout
    assert "--url" in r.stdout
    assert "--site" in r.stdout


def test_cli_url_mode_produces_report(tmp_path):
    """--url mode hits real network (example.com always up)."""
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--url", "https://example.com",
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode in (0, 1), f"unexpected exit: {r.returncode}, stderr={r.stderr}"
    assert (out_dir / "audit-report.json").exists()
    assert (out_dir / "audit-report.md").exists()
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert "sites" in data
    assert len(data["sites"]) == 1
    assert data["sites"][0]["host"] == "https://example.com"


def test_cli_project_with_single_site_unreachable(tmp_path):
    """--project mode with single-site state.yaml runs all hosts.

    primary_domain in single-site fixture is 'simple-project.example.com' — unreachable.
    Audit should still produce a report (with hard-gate fails for unreachable), not crash.
    """
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    (project_dir / ".landing-state.yaml").write_text(
        (FIXTURES / "state-single.yaml").read_text(encoding="utf-8"),
        encoding="utf-8"
    )
    out_dir = project_dir / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--project", str(project_dir),
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    # Expect non-zero (unreachable host = hard-gate fails)
    assert r.returncode in (1, 2), f"expected non-zero for unreachable host, got {r.returncode}"
    if (out_dir / "audit-report.json").exists():
        data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
        assert data["sites"][0]["host"] == "https://simple-project.example.com"


def test_cli_hosts_file_mode(tmp_path):
    """--hosts-file reads URLs from text file (one per line)."""
    hosts_file = tmp_path / "hosts.txt"
    hosts_file.write_text("https://example.com\nhttps://example.org\n", encoding="utf-8")
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--hosts-file", str(hosts_file),
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode in (0, 1)
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert data["total_sites"] == 2
    hosts = {s["host"] for s in data["sites"]}
    assert hosts == {"https://example.com", "https://example.org"}


def test_cli_hosts_file_blank_lines_ignored(tmp_path):
    hosts_file = tmp_path / "hosts.txt"
    hosts_file.write_text("\n\nhttps://example.com\n\n", encoding="utf-8")
    out_dir = tmp_path / "11_QA"
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--hosts-file", str(hosts_file),
         "--out", str(out_dir)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode in (0, 1)
    data = json.loads((out_dir / "audit-report.json").read_text(encoding="utf-8"))
    assert data["total_sites"] == 1


def test_cli_hosts_file_not_found(tmp_path):
    r = subprocess.run(
        [sys.executable, str(RUN_AUDIT),
         "--hosts-file", str(tmp_path / "missing.txt"),
         "--out", str(tmp_path / "out")],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 2
    assert "hosts file" in (r.stderr + r.stdout).lower() or "not found" in (r.stderr + r.stdout).lower()
