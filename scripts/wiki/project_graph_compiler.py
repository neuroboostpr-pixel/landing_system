# scripts/wiki/project_graph_compiler.py
"""Компилит артефакты проекта-лендинга в <project>/wiki/.

В отличие от system_compiler — большинство концептов генерится БЕЗ SDK
(парсинг yaml/json/html → markdown). SDK зовётся только для index.md.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from scripts.wiki import sdk_client, utils
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


def _build_index(state: dict, has_blocks: bool, has_brand: bool) -> str:
    """Зовёт SDK для index.md."""
    prompt = (PROMPTS_DIR / "project_index.md").read_text(encoding="utf-8")
    user = f"""Проект: {state.get('project')}
Текущий этап: {state.get('current_stage')}
Closed: {', '.join(state.get('approved', []))}
In progress: {', '.join(state.get('in_progress', []))}
Locked: {', '.join(state.get('locked', []))}
Концепты доступны: stage-current{', blocks' if has_blocks else ''}{', brand' if has_brand else ''}, photos
"""
    return sdk_client.generate(system=prompt, user=user)


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

    # 5. Index через SDK
    try:
        index_content = _build_index(state, has_blocks, has_brand)
        utils.atomic_write(wiki_dir / "index.md", index_content)
    except sdk_client.SDKError:
        # fallback — простой индекс без SDK
        utils.atomic_write(
            wiki_dir / "index.md",
            f"# {state.get('project', 'project')} wiki\n\nТекущий этап: {state.get('current_stage')}\n",
        )

    # 6. Log
    _append_log(wiki_dir / "log.md", state.get("current_stage", "?"))

    return {
        "current_stage": state.get("current_stage"),
        "concepts_written": ["stage-current.md", "blocks.md", "brand.md", "photos.md"],
    }
