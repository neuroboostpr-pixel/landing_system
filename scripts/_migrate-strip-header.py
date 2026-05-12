#!/usr/bin/env python3
"""Remove the <div class="nu-theme-bar">...</div> block from header.php."""
import re
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    src = f.read()

# DOTALL: the block spans multiple lines.
pattern = re.compile(r"\n?<div class=\"nu-theme-bar\".*?</div>\s*</div>\s*\n", re.DOTALL)
new = pattern.sub("\n", src, count=1)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(new)
