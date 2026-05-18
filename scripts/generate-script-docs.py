#!/usr/bin/env python3
"""Извлекает docstring/header из каждого скрипта в scripts/ и создаёт .md сводку.

Для Python (.py): извлекает module-level docstring (между тройными кавычками)
Для Bash (.sh): извлекает первые ~20 строк комментариев # после shebang

Создаёт <script-name>.<ext>.doc.md в той же папке (рядом со скриптом).
Эти .md потом подхватывает wiki compile (см. scripts/wiki/config.py SYSTEM_SOURCES).

Использование:
    python3 scripts/generate-script-docs.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO / "scripts"


def extract_python_docstring(content: str) -> str | None:
    """Module-level docstring (после shebang/from __future__ import block)."""
    # Триплет-кавычки в начале файла (после возможного shebang + __future__)
    m = re.search(
        r'^(?:#![^\n]*\n)?'
        r'(?:from\s+__future__[^\n]*\n)?'
        r'(?:\s*\n)*'
        r'"""\s*(.*?)"""',
        content,
        re.DOTALL,
    )
    if m:
        return m.group(1).strip()
    # Fallback: первое попавшееся """..."""
    m = re.search(r'"""\s*(.+?)\s*"""', content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_bash_header(content: str) -> str | None:
    """Первые 20 строк комментариев после shebang."""
    lines = content.splitlines()
    if not lines:
        return None
    start = 1 if lines[0].startswith("#!") else 0
    comments: list[str] = []
    for line in lines[start:start + 30]:
        s = line.strip()
        if not s:
            if comments:
                # пустая строка прерывает блок только если уже что-то накопили
                # и следующая строка не комментарий
                continue
            continue
        if s.startswith("#"):
            comments.append(s.lstrip("#").strip())
        elif comments:
            break
    return "\n".join(comments) if comments else None


def process_file(path: Path) -> tuple[Path, str] | None:
    """Возвращает (md_path, content) или None если нечего документировать."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    if path.suffix == ".py":
        doc = extract_python_docstring(content)
        lang = "python"
    elif path.suffix == ".sh":
        doc = extract_bash_header(content)
        lang = "bash"
    else:
        return None

    if not doc or len(doc) < 20:
        return None

    # Sibling .md: foo.py → foo.py.doc.md
    md_path = path.with_suffix(path.suffix + ".doc.md")
    rel = path.relative_to(REPO).as_posix()

    md_content = (
        "---\n"
        f"type: script\n"
        f"name: {path.stem}\n"
        f"language: {lang}\n"
        f'sources: ["{rel}"]\n'
        "updated: 2026-05-18\n"
        "---\n\n"
        f"# {path.name}\n\n"
        f"{doc}\n\n"
        "## Источник\n\n"
        f"- `{rel}`\n"
    )
    return (md_path, md_content)


def main() -> None:
    written = 0
    skipped = 0
    for path in SCRIPTS_DIR.rglob("*.py"):
        # Skip private migration helpers + tests + wiki/__pycache__
        if path.name.startswith("_"):
            skipped += 1
            continue
        if "test" in path.parts or "__pycache__" in path.parts:
            skipped += 1
            continue
        # Не документируем сам генератор и .doc.md hose
        if path.name == "generate-script-docs.py":
            continue
        result = process_file(path)
        if result:
            md_path, content = result
            md_path.write_text(content, encoding="utf-8")
            written += 1
        else:
            skipped += 1

    for path in SCRIPTS_DIR.rglob("*.sh"):
        if "test" in path.parts or "__pycache__" in path.parts:
            skipped += 1
            continue
        result = process_file(path)
        if result:
            md_path, content = result
            md_path.write_text(content, encoding="utf-8")
            written += 1
        else:
            skipped += 1

    print(f"Generated {written} script .doc.md files (skipped {skipped}).")


if __name__ == "__main__":
    main()
