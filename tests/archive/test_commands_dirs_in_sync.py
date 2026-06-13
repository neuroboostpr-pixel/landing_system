"""Страж: commands/ (plugin-дистрибуция) == .claude/commands/ (проектная).

Две папки команд расходились (6 команд пропадали при установке как плагин,
landing-clone/landing-help были устаревшими EN-версиями). Этот тест держит их
синхронными: .claude/commands/ — источник истины.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / ".claude" / "commands"
DST = ROOT / "commands"


def _md(d):
    return {p.name for p in d.glob("*.md")}


def test_same_command_set():
    missing = _md(SRC) - _md(DST)
    extra = _md(DST) - _md(SRC)
    assert not missing and not extra, (
        f"commands/ рассинхронен с .claude/commands/: "
        f"отсутствуют={sorted(missing)} лишние={sorted(extra)}. "
        f"Синхронизируй: cp .claude/commands/*.md commands/")


def test_identical_content():
    diffs = []
    for name in _md(SRC) & _md(DST):
        if (SRC / name).read_text(encoding="utf-8") != (DST / name).read_text(encoding="utf-8"):
            diffs.append(name)
    assert not diffs, (
        f"Содержимое команд расходится между .claude/commands/ и commands/: {sorted(diffs)}. "
        f"Источник истины — .claude/commands/.")
