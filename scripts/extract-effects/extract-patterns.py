#!/usr/bin/env python3
"""Анализирует CSS и извлекает премиум-эффекты.

Что ищем:
- @keyframes (анимации)
- transition: ... (плавные переходы)
- :hover state styles (hover-эффекты)
- @media (prefers-reduced-motion: ...) (правильный motion)
- backdrop-filter / filter (стекло/блюр)
- transform: translate3d / scale / rotate
- clip-path, mask-image
- ::before/::after декоративные элементы
- grid с auto-fit/auto-fill
- container queries
- @scroll-timeline / scroll-driven animations

Usage:
    extract-patterns.py <scraped-dir> [<scraped-dir> ...]

Печатает JSON в stdout: {pattern_name: [match_strings...]}
"""
import re
import sys
import json
from pathlib import Path
from collections import defaultdict


PATTERNS = {
    "keyframes": r"@keyframes\s+([\w-]+)\s*\{[^@]*?\}",
    "transitions": r"transition:\s*([^;]+);",
    "hover_states": r"([^,{}]+):hover\s*\{([^}]+)\}",
    "backdrop_filter": r"backdrop-filter:\s*([^;]+);",
    "scroll_animations": r"@scroll-timeline|animation-timeline|scroll\(\)",
    "clip_path": r"clip-path:\s*([^;]+);",
    "transform_3d": r"transform:\s*[^;]*(?:translate3d|scale|rotate)[^;]*",
    "grid_auto": r"grid-template-columns:\s*repeat\(auto-(?:fit|fill)",
    "motion_safe": r"@media[^{]*prefers-reduced-motion",
    "filter_blur": r"filter:\s*[^;]*blur\(",
    "mix_blend": r"mix-blend-mode:\s*([^;]+);",
    "gradient_complex": r"(?:linear|radial|conic)-gradient\([^)]{50,}\)",
}


def extract(css_text: str) -> dict:
    """Возвращает {pattern_name: [match_strings]}."""
    found = defaultdict(list)
    for name, pattern in PATTERNS.items():
        matches = re.findall(pattern, css_text, re.IGNORECASE | re.DOTALL)
        if matches:
            found[name] = matches[:20]  # лимит 20 примеров
    return dict(found)


def dedupe_patterns(all_findings: list) -> dict:
    """Берёт все findings со всех URL и dedupes по hash."""
    merged = defaultdict(set)
    for findings in all_findings:
        for name, matches in findings.items():
            for m in matches:
                # Hash для дедупа
                snippet = m if isinstance(m, str) else " ".join(str(x) for x in m)
                merged[name].add(snippet[:300])
    return {k: sorted(v)[:30] for k, v in merged.items()}


def main():
    if len(sys.argv) < 2:
        print("Usage: extract-patterns.py <scraped-dir> [<scraped-dir> ...]", file=sys.stderr)
        sys.exit(2)

    all_findings = []
    for d in sys.argv[1:]:
        css_files = list(Path(d).glob("*.css"))
        combined = "\n\n".join(
            f.read_text(encoding="utf-8", errors="ignore") for f in css_files
        )
        findings = extract(combined)
        all_findings.append(findings)

    deduped = dedupe_patterns(all_findings)
    print(json.dumps(deduped, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
