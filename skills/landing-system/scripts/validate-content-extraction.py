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


def check_sections_match(content_file, prototype_file):
    """Check that number of sections match between content.md and prototype.yaml."""
    if not os.path.exists(content_file):
        print(f"FAIL: {content_file} not found")
        return False

    if not os.path.exists(prototype_file):
        print(f"FAIL: {prototype_file} not found")
        return False

    # Count H2 headers in content.md (## Section Name)
    with open(content_file, 'r', encoding='utf-8') as f:
        content_text = f.read()
    content_sections = len(re.findall(r"^##\s", content_text, re.MULTILINE))

    # Count sections in prototype.yaml
    try:
        with open(prototype_file, 'r', encoding='utf-8') as f:
            proto = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"FAIL: Cannot parse {prototype_file}: {e}")
        return False

    yaml_sections = len(proto.get('sections', []))

    if content_sections == yaml_sections:
        print(f"PASS: {content_sections} sections match")
        return True
    else:
        print(f"FAIL: content.md has {content_sections} sections, prototype.yaml has {yaml_sections}")
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
