"""Tests for skills/wp-cli-deployer/scripts/import-redirects.py"""
import importlib.util
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "skills" / "wp-cli-deployer" / "scripts" / "import-redirects.py"

spec = importlib.util.spec_from_file_location("import_redirects", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _write_csv(tmpdir: str, rows: list) -> str:
    path = Path(tmpdir) / "redirects.csv"
    lines = ["source,target,code"] + [f"{s},{t},{c}" for s, t, c in rows]
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def test_parse_valid_csv():
    with tempfile.TemporaryDirectory() as tmpdir:
        csv = _write_csv(tmpdir, [
            ("/old-page", "/new-page", "301"),
            ("/about-us", "/about", "301"),
        ])
        rows = mod.parse_csv(csv)
        assert len(rows) == 2
        assert rows[0]["source"] == "/old-page"
        assert rows[0]["target"] == "/new-page"
        assert rows[0]["code"] == "301"


def test_parse_csv_skips_empty_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "redirects.csv"
        path.write_text("source,target,code\n/a,/b,301\n\n/c,/d,302\n", encoding="utf-8")
        rows = mod.parse_csv(str(path))
        assert len(rows) == 2


def test_validate_rejects_external_source():
    rows = [{"source": "https://external.com/page", "target": "/new", "code": "301"}]
    errors = mod.validate_rows(rows)
    assert any("external" in e.lower() or "source" in e.lower() for e in errors)


def test_validate_rejects_bad_code():
    rows = [{"source": "/old", "target": "/new", "code": "200"}]
    errors = mod.validate_rows(rows)
    assert any("code" in e.lower() or "200" in e for e in errors)


def test_validate_accepts_valid_rows():
    rows = [
        {"source": "/old", "target": "/new", "code": "301"},
        {"source": "/old2", "target": "https://other.com/page", "code": "302"},
    ]
    errors = mod.validate_rows(rows)
    assert errors == []


def test_generate_wp_commands():
    rows = [{"source": "/old", "target": "/new", "code": "301"}]
    cmds = mod.generate_wp_commands(rows, wp_cmd="wp --path=/var/www --allow-root")
    assert len(cmds) == 1
    assert "/old" in cmds[0]
    assert "/new" in cmds[0]
    assert "redirection" in cmds[0].lower() or "redirect" in cmds[0].lower()
