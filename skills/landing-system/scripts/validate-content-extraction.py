#!/usr/bin/env python3
"""
Validator для content.md extraction.

Usage:
  python3 validate-content-extraction.py <content.md> --check-no-lorem
  python3 validate-content-extraction.py <content.md> <prototype.yaml> --check-sections-match
  python3 validate-content-extraction.py <extraction-log.md> --check-log-passed
"""

import sys
import re
import yaml
import os

TEMPLATE_PATTERNS = [
    r"lorem ipsum",
    r"description goes here",
    r"add your text",
    r"your text here",
    r"sample text",
    r"\[placeholder\]",
]

def check_no_lorem(content_file):
    """Check that content.md does not contain generic template patterns."""
    if not os.path.exists(content_file):
        print(f"FAIL: {content_file} not found")
        return False

    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read().lower()

    for pattern in TEMPLATE_PATTERNS:
        if re.search(pattern, content):
            print(f"FAIL: Found template pattern: {pattern}")
            return False
    print("PASS: No template patterns found")
    return True


def _count_md_blocks(md_text):
    """Кол-во блоков в prototype.md — по заголовкам '## ' (## Block N: type)."""
    return len(re.findall(r"^##\s", md_text, re.MULTILINE))


def _count_prototype_units(prototype_file):
    """Кол-во блоков прототипа. A1: канон — prototype.md; yaml опционален.

    - .md   → считаем '## ' заголовки.
    - .yaml → ключ 'blocks' (схема md-to-yaml) или 'sections' (legacy).
              Если yaml отсутствует — fallback на sibling prototype.md.
    Возвращает (count, source_label) или (None, reason) при ошибке.
    """
    path = prototype_file
    if path.endswith(".md"):
        if not os.path.exists(path):
            return None, f"{path} not found"
        with open(path, 'r', encoding='utf-8') as f:
            return _count_md_blocks(f.read()), "prototype.md"

    if not os.path.exists(path):
        md_sibling = os.path.join(os.path.dirname(path), "prototype.md")
        if os.path.exists(md_sibling):
            with open(md_sibling, 'r', encoding='utf-8') as f:
                return _count_md_blocks(f.read()), "prototype.md (fallback)"
        return None, f"нет ни {path}, ни prototype.md"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            proto = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        return None, f"Cannot parse {path}: {e}"
    units = proto.get('blocks')
    if units is None:
        units = proto.get('sections', [])
    return len(units), "prototype.yaml"


def check_sections_match(content_file, prototype_file):
    """Кол-во секций content.md == кол-во блоков прототипа (A1-aware)."""
    if not os.path.exists(content_file):
        print(f"FAIL: {content_file} not found")
        return False

    with open(content_file, 'r', encoding='utf-8') as f:
        content_text = f.read()
    content_sections = len(re.findall(r"^##\s", content_text, re.MULTILINE))

    proto_count, source = _count_prototype_units(prototype_file)
    if proto_count is None:
        print(f"FAIL: {source}")
        return False

    if content_sections == proto_count:
        print(f"PASS: {content_sections} sections match ({source})")
        return True
    print(f"FAIL: content.md has {content_sections} sections, "
          f"{source} has {proto_count}")
    return False


def check_log_passed(log_file):
    """Check that extraction-log.md shows SUCCESS status."""
    if not os.path.exists(log_file):
        print(f"FAIL: {log_file} not found")
        return False

    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if re.search(r"✅ (SUCCESS|PASSED)", content):
        print("PASS: extraction-log shows SUCCESS")
        return True
    else:
        print("FAIL: extraction-log shows failures or not marked as SUCCESS")
        return False


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: validate-content-extraction.py <file> [<file2>] [--check-*]")
        sys.exit(1)

    # Parse arguments
    check_type = None
    files = []

    for arg in args:
        if arg.startswith("--check-"):
            check_type = arg
        else:
            files.append(arg)

    if not check_type:
        print("Error: --check-* flag required")
        sys.exit(1)

    # Execute appropriate check
    success = False

    if check_type == "--check-no-lorem":
        if len(files) < 1:
            print("Error: --check-no-lorem requires 1 file argument")
            sys.exit(1)
        success = check_no_lorem(files[0])

    elif check_type == "--check-sections-match":
        if len(files) < 2:
            print("Error: --check-sections-match requires 2 file arguments")
            sys.exit(1)
        success = check_sections_match(files[0], files[1])

    elif check_type == "--check-log-passed":
        if len(files) < 1:
            print("Error: --check-log-passed requires 1 file argument")
            sys.exit(1)
        success = check_log_passed(files[0])

    else:
        print(f"Error: Unknown check: {check_type}")
        sys.exit(1)

    sys.exit(0 if success else 1)
