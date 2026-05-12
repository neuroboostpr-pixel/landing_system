#!/usr/bin/env python3
"""Remove initThemeSwitcher function and its invocation from main.js."""
import re
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    src = f.read()

# Strip function declaration up through its closing brace.
# Match: function initThemeSwitcher() { ... }  (balanced by counting in regex is hard;
# use a hand-rolled scan that finds the matching brace.)
def strip_function(src, name):
    idx = src.find("function " + name)
    if idx < 0:
        return src
    brace_idx = src.find("{", idx)
    if brace_idx < 0:
        return src
    depth = 0
    i = brace_idx
    while i < len(src):
        c = src[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                # Eat a trailing newline if present.
                if end < len(src) and src[end] == "\n":
                    end += 1
                return src[:idx] + src[end:]
        i += 1
    return src

src = strip_function(src, "initThemeSwitcher")
# Strip any line that calls initThemeSwitcher(), with or without leading whitespace.
src = re.sub(r"^\s*initThemeSwitcher\(\);.*\n", "", src, flags=re.MULTILINE)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(src)
