"""A1 (зона A): все файловые операции в скриптах прототипа — с encoding=.

Спека reference-driven flow §2.1: «скрипты разбора падают на русском тексте
под Windows (нет указания кодировки utf-8) — починить во всех скриптах».

AST-скан: каждый вызов read_text()/write_text()/open() в перечисленных
скиллах обязан передавать keyword `encoding` (бинарные режимы 'rb'/'wb'
исключение).
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCAN_GLOBS = [
    "skills/prototype-import/scripts/*.py",
    "skills/block-composition/scripts/*.py",
]


def _violations_in(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Attribute) and func.attr in ("read_text", "write_text"):
            name = func.attr
        elif isinstance(func, ast.Name) and func.id == "open":
            name = "open"
        if name is None:
            continue
        kwargs = {k.arg for k in node.keywords}
        if "encoding" in kwargs:
            continue
        # open(..., 'rb'/'wb') — бинарный режим, encoding не нужен
        if name == "open" and len(node.args) >= 2:
            mode = node.args[1]
            if isinstance(mode, ast.Constant) and "b" in str(mode.value):
                continue
        out.append(f"{path.relative_to(ROOT)}:{node.lineno}: {name}() без encoding=")
    return out


def test_all_file_io_has_encoding():
    violations = []
    for pattern in SCAN_GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            violations.extend(_violations_in(p))
    assert not violations, "Файловый I/O без encoding= (упадёт на Windows):\n" + "\n".join(violations)
