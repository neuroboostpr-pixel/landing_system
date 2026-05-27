"""Pure-Python filter over wiki/index.yaml.

CLI:
    python -m scripts.wiki.query --stage=08 --type=agent
    python -m scripts.wiki.query --tag=wordpress
    python -m scripts.wiki.query --slug=block-composer
    python -m scripts.wiki.query --trigger=landing-build
    python -m scripts.wiki.query --grep=gutenberg
    python -m scripts.wiki.query --slug=X --format=cards

Formats: compact (default), cards, slugs, json.
No SDK calls. <100ms for any query.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.wiki import config


def _load_index(wiki_dir: Path) -> dict[str, Any]:
    index_yaml = wiki_dir / "index.yaml"
    if not index_yaml.exists():
        return {"version": 1, "concepts": []}
    try:
        return yaml.safe_load(index_yaml.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {"version": 1, "concepts": []}


def filter_concepts(
    wiki_dir: Path,
    *,
    stage: str | None = None,
    type_: str | None = None,
    tag: str | None = None,
    trigger: str | None = None,
    slug: str | None = None,
    grep: str | None = None,
) -> list[dict[str, Any]]:
    """Возвращает список концептов из index.yaml, удовлетворяющих фильтрам."""
    data = _load_index(wiki_dir)
    result: list[dict[str, Any]] = []
    for c in data.get("concepts", []):
        if slug is not None and c.get("slug") != slug:
            continue
        if stage is not None and c.get("stage") != stage:
            continue
        if type_ is not None and c.get("type") != type_:
            continue
        if tag is not None and tag not in (c.get("tags") or []):
            continue
        if trigger is not None and trigger not in (c.get("triggers") or []):
            continue
        if grep is not None:
            haystack = " ".join(
                str(c.get(k, "")) for k in ("slug", "name", "tags", "triggers")
            ).lower()
            if grep.lower() not in haystack:
                continue
        result.append(c)
    return result


def _format_compact(concepts: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for c in concepts:
        tags = ",".join(c.get("tags") or [])
        triggers = ",".join(c.get("triggers") or [])
        head = f"[[{c.get('slug', '?')}]]"
        if tags:
            head += f" | tags: {tags}"
        if triggers:
            head += f" | triggers: {triggers}"
        lines.append(head)
        name = c.get("name", c.get("slug", ""))
        if name and name != c.get("slug"):
            lines.append(f"  {name}")
        if c.get("card"):
            lines.append(f"  card: {c['card']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _format_slugs(concepts: list[dict[str, Any]]) -> str:
    return "\n".join(c.get("slug", "") for c in concepts) + "\n"


def _format_json(concepts: list[dict[str, Any]]) -> str:
    return json.dumps(concepts, ensure_ascii=False, indent=2)


def _format_cards(wiki_dir: Path, concepts: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for c in concepts:
        card_rel = c.get("card")
        if not card_rel:
            continue
        card_path = wiki_dir / card_rel
        if card_path.exists():
            chunks.append(card_path.read_text(encoding="utf-8"))
    return "\n\n---\n\n".join(chunks) + "\n"


def format_output(
    wiki_dir: Path, concepts: list[dict[str, Any]], fmt: str = "compact"
) -> str:
    if fmt == "compact":
        return _format_compact(concepts)
    if fmt == "slugs":
        return _format_slugs(concepts)
    if fmt == "json":
        return _format_json(concepts)
    if fmt == "cards":
        return _format_cards(wiki_dir, concepts)
    raise ValueError(f"Unknown format: {fmt}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query wiki/index.yaml — pure-Python filter, no SDK."
    )
    parser.add_argument("--wiki", default=str(config.WIKI_DIR), help="wiki/ dir")
    parser.add_argument("--stage", help="Filter by stage (e.g. 08)")
    parser.add_argument("--type", dest="type_", help="Filter by type")
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument("--trigger", help="Filter by trigger")
    parser.add_argument("--slug", help="Filter by exact slug")
    parser.add_argument("--grep", help="Substring search across slug/name/tags/triggers")
    parser.add_argument(
        "--format", dest="fmt", default="compact",
        choices=("compact", "cards", "slugs", "json"),
    )
    args = parser.parse_args()
    wiki_dir = Path(args.wiki).resolve()

    concepts = filter_concepts(
        wiki_dir,
        stage=args.stage,
        type_=args.type_,
        tag=args.tag,
        trigger=args.trigger,
        slug=args.slug,
        grep=args.grep,
    )
    # Логируем wiki query (silent если routing_log недоступен)
    try:
        import os
        from scripts.wiki import routing_log
        session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")
        filters_dict = {
            "stage": args.stage,
            "type": args.type_,
            "tag": args.tag,
            "trigger": args.trigger,
            "slug": args.slug,
            "grep": args.grep,
        }
        est_saved = routing_log.estimate_tokens_saved(wiki_dir, concepts)
        routing_log.log_query(session_id, filters_dict, [c["slug"] for c in concepts], est_saved)
    except Exception as e:
        print(f"[wiki routing_log] failed to log: {e}", file=sys.stderr)

    sys.stdout.write(format_output(wiki_dir, concepts, fmt=args.fmt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
