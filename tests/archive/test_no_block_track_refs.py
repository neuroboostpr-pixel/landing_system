"""E2: блочный трек в архиве — живой код не должен на него ссылаться.

Сканируются исполняемые/конфигурационные зоны. docs/, wiki/, archive/ —
вне скоупа (история легальна). skills/block-composition исключён осознанно:
переходный код, переписывается в Zone C (см. план Phase 1, решения).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ["agents", "skills", "scripts", "commands", ".claude/commands",
             "config", "template"]
SCAN_FILES = ["CLAUDE.md"]
# wiki: компилятор project-graph парсит артефакты СТАРЫХ проектов
# (07a_WIREFRAME/selections.yaml и т.п.) — это история, не живой пайплайн.
EXCLUDE_PARTS = {"block-composition", "worktrees", "node_modules", "__pycache__",
                 "wiki"}

FORBIDDEN = [
    "skills/wireframe-rendering",
    "skills/landing-import-blocks",
    "skills/block-library-management",
    "render-wireframe.py",
    "match-candidates.py",
    "generate-gallery.py",
    "normalize-block-templates.py",
    "block-library/catalog.yaml",
    "block-library/taxonomy.yaml",
    "landing-wireframe",
    "landing-import-blocks",
    "ux-composer",
    "07b_wireframe",
    "07a_WIREFRAME",
    "07a_wireframe",        # lowercase-форма тоже запрещена (была дырой в guard)
    "wireframe.html",
    "wireframe selections",
]

EXTS = {".md", ".py", ".sh", ".yaml", ".yml", ".html", ".json", ".bats"}


def _iter_files():
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in EXTS and not (EXCLUDE_PARTS & set(p.parts)):
                yield p
    for f in SCAN_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def test_no_references_to_archived_block_track():
    violations = []
    for p in _iter_files():
        text = p.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN:
            if token in text:
                violations.append(f"{p.relative_to(ROOT)}: {token}")
    assert not violations, (
        "Живой код ссылается на архивированный блочный трек:\n" + "\n".join(violations)
    )
