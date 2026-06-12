"""Tests for skills/wp-cli-deployer/scripts/get-deploy-target.py"""
import importlib.util
import tempfile
from pathlib import Path
import yaml

SCRIPT = Path(__file__).parents[2] / "skills" / "wp-cli-deployer" / "scripts" / "get-deploy-target.py"

spec = importlib.util.spec_from_file_location("get_deploy_target", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _write_targets(tmpdir: str) -> str:
    path = Path(tmpdir) / "deploy-targets.yaml"
    data = {
        "staging": {
            "beget_user": "staging_user",
            "beget_host": "staging.example.com",
            "beget_path": "/home/staging_user/public_html/staging",
        },
        "prod": {
            "beget_user": "prod_user",
            "beget_host": "example.com",
            "beget_path": "/home/prod_user/public_html",
        },
    }
    path.write_text(yaml.dump(data), encoding="utf-8")
    return str(path)


def test_staging_target_returned():
    with tempfile.TemporaryDirectory() as tmpdir:
        targets = _write_targets(tmpdir)
        result = mod.get_target(targets, "staging")
        assert result["beget_user"] == "staging_user"
        assert result["beget_host"] == "staging.example.com"


def test_prod_target_returned():
    with tempfile.TemporaryDirectory() as tmpdir:
        targets = _write_targets(tmpdir)
        result = mod.get_target(targets, "prod")
        assert result["beget_host"] == "example.com"
        assert result["beget_path"] == "/home/prod_user/public_html"


def test_unknown_env_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        targets = _write_targets(tmpdir)
        try:
            mod.get_target(targets, "unknown")
            assert False, "should raise"
        except SystemExit as exc:
            assert exc.code != 0
        except ValueError:
            pass  # also acceptable


def test_missing_file_exits_nonzero():
    try:
        mod.get_target("/nonexistent/deploy-targets.yaml", "staging")
        assert False, "should raise"
    except SystemExit as exc:
        assert exc.code != 0


def test_print_env_vars_format():
    with tempfile.TemporaryDirectory() as tmpdir:
        targets = _write_targets(tmpdir)
        lines = mod.format_env_exports(mod.get_target(targets, "staging"))
        joined = "\n".join(lines)
        assert "BEGET_USER=" in joined
        assert "BEGET_HOST=" in joined
        assert "BEGET_PATH=" in joined
