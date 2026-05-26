"""Smoke-тесты хуков — что они принимают пустой stdin и не падают."""
import json
import subprocess
import sys
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[2] / "scripts" / "wiki" / "hooks"


def test_session_start_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input="{}",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_session_start_invalid_json():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0  # не падает на мусоре


def test_session_end_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_end.py")],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0


def test_pre_compact_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "pre_compact.py")],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0


def test_session_start_injects_landing_system_index(tmp_path, monkeypatch):
    """Когда cwd = landing-system/ и wiki/index.yaml есть — в выводе должен быть wiki_runtime hint."""
    import yaml
    repo = Path(__file__).resolve().parents[2]
    index_yaml = repo / "wiki" / "index.yaml"
    created_fake = False
    if not index_yaml.exists():
        fake_data = {"version": 1, "counts": {"total": 5, "by_type": {"agent": 5}}, "concepts": []}
        index_yaml.write_text(yaml.safe_dump(fake_data), encoding="utf-8")
        created_fake = True
    try:
        payload = {"cwd": str(repo)}
        result = subprocess.run(
            [sys.executable, str(HOOKS / "session_start.py")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "<wiki_runtime>" in result.stdout
        assert "<system_wiki_index>" not in result.stdout
    finally:
        if created_fake:
            index_yaml.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# New tests: 50-token hint behaviour
# ---------------------------------------------------------------------------

HOOK = Path(__file__).resolve().parents[2] / "scripts" / "wiki" / "hooks" / "session_start.py"


def _run_hook(cwd: str, env_overrides: dict | None = None) -> str:
    """Invoke hook as subprocess with given cwd in stdin payload."""
    import os
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"cwd": cwd}),
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.stdout


def test_hook_emits_wiki_hint_not_full_index():
    """Hook должен печатать <wiki_runtime> hint вместо полного index.md."""
    import yaml
    landing_system = Path(__file__).resolve().parents[2]
    wiki_dir = landing_system / "wiki"
    index_yaml = wiki_dir / "index.yaml"
    created_fake = False
    if not index_yaml.exists():
        # Create minimal fake index.yaml for the test
        fake_data = {"version": 1, "counts": {"total": 5, "by_type": {"agent": 5}}, "concepts": []}
        index_yaml.write_text(yaml.safe_dump(fake_data), encoding="utf-8")
        created_fake = True

    try:
        output = _run_hook(cwd=str(landing_system))
        assert "<wiki_runtime>" in output
        assert "index.yaml" in output
        assert "scripts.wiki.query" in output or "scripts/wiki/query" in output
        # The big system_wiki_index block must NOT appear
        assert "<system_wiki_index>" not in output
    finally:
        if created_fake:
            index_yaml.unlink(missing_ok=True)


def test_hook_returns_no_wiki_hint_when_no_yaml(tmp_path):
    """Если index.yaml нет в cwd — wiki hint не выдаётся."""
    # Use a directory that has no wiki/index.yaml
    output = _run_hook(cwd=str(tmp_path))
    assert "<wiki_runtime>" not in output
