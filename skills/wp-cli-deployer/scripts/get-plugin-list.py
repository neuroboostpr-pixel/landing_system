#!/usr/bin/env python3
# skills/wp-cli-deployer/scripts/get-plugin-list.py
# Merge wordpress.plugins from design-stack.yaml with DEFAULT_PLUGINS.
# Prints one plugin slug per line (for use in deploy-wordpress.sh).
# Usage: python get-plugin-list.py <design-stack.yaml>
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

DEFAULT_PLUGINS = [
    "litespeed-cache",
    "shortpixel-image-optimiser",
    "wordfence",
    "updraftplus",
    "limit-login-attempts-reloaded",
    "redirection",
    "really-simple-ssl",
]


def get_plugin_list(stack_path: str) -> list:
    """Return merged list of plugin slugs (stack + defaults, no duplicates)."""
    stack_plugins = []
    path = Path(stack_path)
    if path.is_file() and yaml is not None:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            wp = data.get("wordpress") or {}
            stack_plugins = [str(p) for p in (wp.get("plugins") or [])]
        except (yaml.YAMLError, OSError):
            pass

    seen = set()
    result = []
    for slug in stack_plugins + DEFAULT_PLUGINS:
        if slug not in seen:
            seen.add(slug)
            result.append(slug)
    return result


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: get-plugin-list.py <design-stack.yaml>", file=sys.stderr)
        return 1
    for slug in get_plugin_list(sys.argv[1]):
        print(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
