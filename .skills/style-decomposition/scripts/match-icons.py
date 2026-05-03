#!/usr/bin/env python3
"""Match semantic icon names to Iconify icon libraries.

CLI: python3 match-icons.py <output-yaml> --need check arrow-right user
"""
import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.adapters.iconify import search
from tools.logger import success, error

_TARGET_LIBRARIES = ["lucide", "phosphor", "heroicons", "tabler", "material-symbols"]


def match_icons(
    needed: List[str],
    output_yaml: str,
    library_filter: Optional[str] = None,
) -> dict:
    """Search Iconify for each needed icon name; group by prefix; recommend library.

    Args:
        needed: list of semantic icon names (e.g. ["check", "arrow-right"])
        output_yaml: path to write icons.yaml
        library_filter: optional prefix to restrict search (e.g. "lucide")

    Returns dict matching the output yaml structure.
    """
    matches: Dict[str, List[str]] = {}
    library_hits: Counter = Counter()

    for name in needed:
        results = search(name, limit=32, prefix=library_filter or "")
        icon_ids = [r["id"] for r in results]
        # Filter to target libraries only
        filtered = [i for i in icon_ids if i.split(":")[0] in _TARGET_LIBRARIES]
        matches[name] = filtered
        for icon_id in filtered:
            library_hits[icon_id.split(":")[0]] += 1

    # Recommend library with most matches across needed icons
    recommendation = _recommend(needed, matches, library_hits)

    out_data = {
        "needed": needed,
        "matches": matches,
        "recommendation": recommendation,
    }

    out = Path(output_yaml)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(out_data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    success(f"Wrote {out}")
    return out_data


def _recommend(needed: List[str], matches: Dict[str, List[str]], library_hits: Counter) -> dict:
    """Pick the library that covers the most needed icons."""
    if not library_hits:
        return {"library": "lucide", "reason": "default — no search results found"}

    # Count how many needed icons each library covers (has at least one match)
    coverage: Counter = Counter()
    for name in needed:
        libs_for_name = {i.split(":")[0] for i in matches.get(name, [])}
        for lib in libs_for_name:
            if lib in _TARGET_LIBRARIES:
                coverage[lib] += 1

    best_lib = coverage.most_common(1)[0][0] if coverage else library_hits.most_common(1)[0][0]
    covered = coverage.get(best_lib, 0)
    total = len(needed)
    reason = f"covers {covered}/{total} needed icons with consistent style"

    return {"library": best_lib, "reason": reason}


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("output_yaml")
    p.add_argument("--need", nargs="+", default=["check", "arrow-right", "user", "x", "sparkles", "shield"])
    p.add_argument("--library", default=None)
    args = p.parse_args(argv[1:])
    try:
        match_icons(args.need, args.output_yaml, args.library)
        return 0
    except Exception as exc:
        error(f"icon matching failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
