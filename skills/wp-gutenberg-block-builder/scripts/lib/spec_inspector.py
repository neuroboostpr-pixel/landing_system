"""Wrap block_spec.load() to expose a flat structure for linting."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from block_spec import load as _load, validate as _validate


@dataclass
class InspectedControl:
    name: str
    type: str
    has_default: bool
    default_value: object


@dataclass
class InspectedSpecBlock:
    slug: str
    probe_selector: Optional[str]
    probe_kind: str
    type: str
    controls: list[InspectedControl] = field(default_factory=list)
    card_controls: list[InspectedControl] = field(default_factory=list)
    template: list[dict] = field(default_factory=list)


@dataclass
class InspectedSpec:
    blocks: list[InspectedSpecBlock]


def _to_inspected_control(c) -> InspectedControl:
    return InspectedControl(
        name=c.name,
        type=c.type,
        has_default=c.default is not None and c.default != "",
        default_value=c.default,
    )


def inspect_spec(spec_path: Path) -> InspectedSpec:
    raw = _load(spec_path)
    _validate(raw)
    blocks: list[InspectedSpecBlock] = []
    for b in raw.blocks:
        card_controls: list[InspectedControl] = []
        template: list[dict] = []
        if b.card is not None:
            card_controls = [_to_inspected_control(c) for c in b.card.controls]
            template = list(b.card.template or [])
        blocks.append(InspectedSpecBlock(
            slug=b.slug,
            probe_selector=b.probe_selector,
            probe_kind=b.probe_kind,
            type=b.type,
            controls=[_to_inspected_control(c) for c in b.controls],
            card_controls=card_controls,
            template=template,
        ))
    return InspectedSpec(blocks=blocks)
