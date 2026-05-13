"""Loader + валидатор для stage-08 block-spec.yaml."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from control_types import (
    ALLOWED_BLOCK_TYPES,
    ALLOWED_CONTROL_TYPES,
    RESERVED_ATTRIBUTE_NAMES,
)


class BlockSpecError(ValueError):
    """Поднимается когда block-spec.yaml некорректен или не проходит валидацию."""


@dataclass
class Control:
    id: str
    name: str
    type: str
    label: str
    default: Optional[object] = None  # accepts str, bool, int — YAML-native types
    child_of: Optional[str] = None
    options: dict = field(default_factory=dict)


@dataclass
class Card:
    slug: str
    title: str
    controls: list[Control] = field(default_factory=list)
    template: list[dict] = field(default_factory=list)


@dataclass
class Block:
    slug: str
    type: str
    title: str
    icon: str
    category: str
    controls: list[Control] = field(default_factory=list)
    section_grid_class: Optional[str] = None
    card: Optional[Card] = None


@dataclass
class Page:
    title: str
    slug: str


@dataclass
class BlockSpec:
    version: int
    page: Page
    blocks: list[Block] = field(default_factory=list)


def _control_from(raw: dict) -> Control:
    return Control(
        id=raw["id"],
        name=raw["name"],
        type=raw["type"],
        label=raw["label"],
        default=raw.get("default"),
        child_of=raw.get("child_of"),
        options=raw.get("options") or {},
    )


def load(path: Path | str) -> BlockSpec:
    p = Path(path)
    if not p.exists():
        raise BlockSpecError(f"block-spec.yaml not found: {p}")
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise BlockSpecError(f"YAML parse error in {p}: {e}") from e
    if not isinstance(data, dict):
        raise BlockSpecError("block-spec.yaml must be a mapping at top level")
    page = data.get("page") or {}
    blocks_raw = data.get("blocks") or []
    if not isinstance(blocks_raw, list):
        raise BlockSpecError("'blocks' must be a list")
    blocks = []
    for b in blocks_raw:
        if not isinstance(b, dict):
            raise BlockSpecError(f"block entry must be a mapping, got {type(b).__name__}")
        card_raw = b.get("card")
        card = None
        if card_raw:
            card = Card(
                slug=card_raw["slug"],
                title=card_raw["title"],
                controls=[_control_from(c) for c in (card_raw.get("controls") or [])],
                template=list(card_raw.get("template") or []),
            )
        blocks.append(Block(
            slug=b["slug"],
            type=b["type"],
            title=b["title"],
            icon=b.get("icon", "block-default"),
            category=b.get("category", "lp-blocks"),
            controls=[_control_from(c) for c in (b.get("controls") or [])],
            section_grid_class=b.get("section_grid_class"),
            card=card,
        ))
    return BlockSpec(
        version=int(data.get("version", 0)),
        page=Page(title=page.get("title", ""), slug=page.get("slug", "home")),
        blocks=blocks,
    )


def _validate_controls(block_label: str, controls: list[Control]) -> None:
    ids: set[str] = set()
    repeater_ids: set[str] = set()
    for c in controls:
        if c.id in ids:
            raise BlockSpecError(f"{block_label}: duplicate control id '{c.id}'")
        ids.add(c.id)
        if c.type not in ALLOWED_CONTROL_TYPES:
            raise BlockSpecError(f"{block_label}: control '{c.id}' has unknown type '{c.type}'")
        if c.name in RESERVED_ATTRIBUTE_NAMES:
            raise BlockSpecError(f"{block_label}: control '{c.id}' uses reserved attribute name '{c.name}'")
        if c.type == "repeater":
            repeater_ids.add(c.id)
    for c in controls:
        if c.child_of is None:
            continue
        if c.child_of not in ids:
            raise BlockSpecError(f"{block_label}: control '{c.id}' child_of='{c.child_of}' does not exist")
        if c.child_of not in repeater_ids:
            raise BlockSpecError(f"{block_label}: control '{c.id}' child_of='{c.child_of}' is not a repeater")
        if c.type == "repeater":
            raise BlockSpecError(
                f"{block_label}: control '{c.id}' is a nested repeater "
                "(repeater inside repeater) — Lazy Blocks does not support this; "
                "split into a section+card pair instead"
            )


def validate(spec: BlockSpec) -> None:
    if spec.version != 1:
        raise BlockSpecError(f"unsupported version {spec.version}; expected 1")
    seen_slugs: set[str] = set()
    for b in spec.blocks:
        if b.slug in seen_slugs:
            raise BlockSpecError(f"duplicate block slug '{b.slug}'")
        seen_slugs.add(b.slug)
        if b.type not in ALLOWED_BLOCK_TYPES:
            raise BlockSpecError(f"block '{b.slug}': unknown type '{b.type}'")
        if b.type == "section-card":
            if b.card is None:
                raise BlockSpecError(f"block '{b.slug}': type=section-card requires 'card:' sub-object")
            if not b.section_grid_class:
                raise BlockSpecError(f"block '{b.slug}': type=section-card requires section_grid_class")
        else:
            if b.card is not None:
                raise BlockSpecError(f"block '{b.slug}': type=single must not have 'card:' sub-object")
            if b.section_grid_class is not None:
                raise BlockSpecError(f"block '{b.slug}': type=single must not have section_grid_class")
        _validate_controls(f"block '{b.slug}'", b.controls)
        if b.card is not None:
            _validate_controls(f"block '{b.slug}'.card", b.card.controls)
