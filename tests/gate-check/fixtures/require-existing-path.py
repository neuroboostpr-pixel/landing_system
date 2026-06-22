#!/usr/bin/env python3
"""Fail unless the first argument is one intact existing path."""
from pathlib import Path
import sys


if len(sys.argv) != 2:
    print(f"expected exactly 1 arg, got {len(sys.argv) - 1}: {sys.argv[1:]}", file=sys.stderr)
    sys.exit(1)

path = Path(sys.argv[1])
if not path.exists():
    print(f"path does not exist: {path}", file=sys.stderr)
    sys.exit(1)
