"""Tests for skills/wp-cli-deployer/scripts/get-plugin-list.py"""
import importlib.util
import tempfile
from pathlib import Path
import yaml

SCRIPT = Path(__file__).parents[2] / "skills" / "wp-cli-deployer" / "scripts" / "get-plugin-list.py"

spec = importlib.util.spec_from_file_location("get_plugin_list", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def write_stack(tmpdir: str, plugins: list) -> str:
    path = Path(tmpdir) / "design-stack.yaml"
    path.write_text(yaml.dump({"mode": "standard", "wordpress": {"plugins": plugins}}), encoding="utf-8")
    return str(path)


def test_default_plugins_always_included():
    with tempfile.TemporaryDirectory() as tmpdir:
        stack = write_stack(tmpdir, [])
        result = mod.get_plugin_list(stack)
        for slug in mod.DEFAULT_PLUGINS:
            assert slug in result, f"{slug} missing from result"


def test_stack_plugins_merged():
    with tempfile.TemporaryDirectory() as tmpdir:
        stack = write_stack(tmpdir, ["fluentform", "lazy-blocks"])
        result = mod.get_plugin_list(stack)
        assert "fluentform" in result
        assert "lazy-blocks" in result


def test_no_duplicates():
    with tempfile.TemporaryDirectory() as tmpdir:
        # wordfence is in DEFAULT_PLUGINS; also in stack
        stack = write_stack(tmpdir, ["wordfence"])
        result = mod.get_plugin_list(stack)
        assert result.count("wordfence") == 1


def test_missing_stack_file_returns_defaults():
    result = mod.get_plugin_list("/nonexistent/design-stack.yaml")
    assert result == mod.DEFAULT_PLUGINS


def test_returns_list_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        stack = write_stack(tmpdir, ["fluentform"])
        result = mod.get_plugin_list(stack)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)
