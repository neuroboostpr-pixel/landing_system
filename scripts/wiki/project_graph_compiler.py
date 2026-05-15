# scripts/wiki/project_graph_compiler.py
"""Компилит артефакты проекта-лендинга в <project>/wiki/.

Все артефакты, включая index.md, генерятся БЕЗ SDK (парсинг yaml/json/html →
markdown). SDK раньше звался для index.md, но выдавал мусор и путал имя
проекта — заменён на детерминированный stub.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from scripts.wiki import utils
from scripts.wiki.parsers import (
    state_yaml,
    selections_yaml,
    tokens_json,
    composed_html,
)

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _stage_current_md(state: dict) -> str:
    stages_md = "\n".join(
        f"- {s}" for s in state.get("approved", [])
    )
    return f"""---
type: project-state
name: stage-current
updated: {date.today().isoformat()}
---

# Текущее состояние проекта

**Проект:** `{state.get('project', '')}`
**Текущий этап:** `{state.get('current_stage', '?')}`

## Закрытые этапы
{stages_md or '_(нет)_'}

## В работе
{chr(10).join('- ' + s for s in state.get('in_progress', [])) or '_(нет)_'}

## Заблокированные
{chr(10).join('- ' + s for s in state.get('locked', [])) or '_(нет)_'}
"""


def _blocks_md(selections: dict) -> str:
    blocks = selections.get("blocks", {})
    if not blocks:
        return ""
    lines = "\n".join(f"- **{slot}**: `{block_id}`" for slot, block_id in blocks.items())
    return f"""---
type: project-blocks
name: blocks
updated: {date.today().isoformat()}
---

# Выбранные блоки

{lines}
"""


def _brand_md(tokens: dict) -> str:
    colors = tokens.get("colors", {})
    fonts = tokens.get("fonts", {})
    colors_lines = "\n".join(f"- **{k}**: `{v}`" for k, v in colors.items())
    fonts_lines = "\n".join(f"- **{k}**: `{v}`" for k, v in fonts.items())
    return f"""---
type: project-brand
name: brand
updated: {date.today().isoformat()}
---

# Бренд

## Цвета
{colors_lines or '_(пусто)_'}

## Шрифты
{fonts_lines or '_(пусто)_'}
"""


def _photos_md(composed: dict) -> str:
    refs = composed.get("photo_references", [])
    if not refs:
        return ""
    lines = "\n".join(f"- `{r}`" for r in refs)
    return f"""---
type: project-photos
name: photos
updated: {date.today().isoformat()}
---

# Фото в проекте

{lines}
"""


def _append_log(log_path: Path, stage: str) -> None:
    today = date.today().isoformat()
    entry = f"\n## [{today}] compile --source-mode=project-graph\n- updated for stage `{stage}`\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


STATUS_EMOJI = {
    "approved": "✅",
    "in_progress": "🔄",
    "locked": "🔒",
    "failed": "❌",
    "n/a": "⏭",
}


def _build_index(state: dict, has_blocks: bool, has_brand: bool) -> str:
    """Stub-генератор index.md проекта БЕЗ SDK.

    Раньше зовёл sdk_client.generate, но SDK для project-индекса выдавал
    мусор (мета-комментарии) и иногда путал имя проекта. Stub надёжнее
    и бесплатно.
    """
    project = state.get("project", "?")
    current = state.get("current_stage", "?")
    approved = state.get("approved", [])
    in_progress = state.get("in_progress", [])
    locked = state.get("locked", [])
    failed = state.get("failed", [])

    total = len(approved) + len(in_progress) + len(locked) + len(failed)

    lines = [
        f"# {project} — wiki проекта",
        "",
        "> Авто-граф проекта. Обновляется после каждого этапа pipeline. Не редактируй вручную.",
        "",
        "## Текущее состояние",
        f"- **Текущий этап:** `{current}`",
        f"- **Закрыто этапов:** {len(approved)} из {total}",
        f"- **Обновлено:** {date.today().isoformat()}",
        "",
        "## Этапы",
    ]

    # Все этапы в порядке: approved → in_progress → locked → failed
    for stage in approved:
        lines.append(f"- {STATUS_EMOJI['approved']} `{stage}` — approved")
    for stage in in_progress:
        lines.append(f"- {STATUS_EMOJI['in_progress']} `{stage}` — in_progress")
    for stage in locked:
        lines.append(f"- {STATUS_EMOJI['locked']} `{stage}` — locked")
    for stage in failed:
        lines.append(f"- {STATUS_EMOJI['failed']} `{stage}` — failed")

    lines.extend(["", "## Связанные документы"])
    lines.append("- [[stage-current]] — детали текущего этапа")
    if has_blocks:
        lines.append("- [[blocks]] — выбранные блоки сайта")
    if has_brand:
        lines.append("- [[brand]] — цвета и шрифты")
    lines.append("- [[photos]] — соответствие фото слотам")

    return "\n".join(lines) + "\n"


def compile_project(project_root: Path) -> dict[str, Any]:
    """Компилит артефакты проекта в <project>/wiki/."""
    wiki_dir = project_root / "wiki"
    concepts_dir = wiki_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    # 1. .landing-state.yaml → stage-current.md
    state_path = project_root / ".landing-state.yaml"
    if not state_path.exists():
        raise FileNotFoundError(f"{state_path} not found")
    state = state_yaml.parse(state_path)
    # Fallback: если поле project в .landing-state.yaml не заполнено,
    # берём имя папки проекта (надёжный источник).
    if not state.get("project"):
        state["project"] = project_root.name
    utils.atomic_write(concepts_dir / "stage-current.md", _stage_current_md(state))

    # 2. wireframe selections → blocks.md (опционально)
    has_blocks = False
    selections_path = project_root / "07a_WIREFRAME" / "selections.yaml"
    if selections_path.exists():
        selections = selections_yaml.parse(selections_path)
        md = _blocks_md(selections)
        if md:
            utils.atomic_write(concepts_dir / "blocks.md", md)
            has_blocks = True

    # 3. tokens → brand.md
    has_brand = False
    tokens_path = project_root / "04_БРЕНД" / "tokens.json"
    if tokens_path.exists():
        tokens = tokens_json.parse(tokens_path)
        utils.atomic_write(concepts_dir / "brand.md", _brand_md(tokens))
        has_brand = True

    # 4. composed.html → photos.md
    composed_path = project_root / "07b_COMPOSED" / "composed.html"
    if composed_path.exists():
        composed = composed_html.parse(composed_path)
        md = _photos_md(composed)
        if md:
            utils.atomic_write(concepts_dir / "photos.md", md)

    # 5. Index (stub, без SDK)
    index_content = _build_index(state, has_blocks, has_brand)
    utils.atomic_write(wiki_dir / "index.md", index_content)

    # 6. Log
    _append_log(wiki_dir / "log.md", state.get("current_stage", "?"))

    return {
        "current_stage": state.get("current_stage"),
        "concepts_written": ["stage-current.md", "blocks.md", "brand.md", "photos.md"],
    }
