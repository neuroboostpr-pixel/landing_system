"""Parse composed.html into a tree of inspection facts.

Returns one InspectedBlock per probe selector. Each InspectedBlock has
0..N InspectedMatch entries (one per DOM element that matched).

Heuristics for child analysis live in lint_heuristics.py; this module
only handles DOM parsing and probe matching.
"""
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class InspectedChild:
    heuristic: str
    count: int
    values: list[str] = field(default_factory=list)


@dataclass
class InspectedMatch:
    tag: str
    attrs: dict
    soup: object  # BeautifulSoup Tag — passed to heuristics
    children: list[InspectedChild] = field(default_factory=list)


@dataclass
class InspectedBlock:
    probe_selector: str
    matches: list[InspectedMatch] = field(default_factory=list)


def inspect(composed_path: Path, probes: list[str]) -> list[InspectedBlock]:
    html = composed_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for probe in probes:
        block = InspectedBlock(probe_selector=probe)
        for el in soup.select(probe):
            block.matches.append(InspectedMatch(
                tag=el.name,
                attrs=dict(el.attrs),
                soup=el,
            ))
        result.append(block)
    return result
