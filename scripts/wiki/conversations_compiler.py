# scripts/wiki/conversations_compiler.py
"""Компилит daily/ → memory/compiled/concepts/.

Зовётся хуком SessionEnd или вручную:
  python -m scripts.wiki.compile --source-mode=conversations --project=<slug>
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts.wiki import sdk_client, utils

PROMPTS_DIR = Path(__file__).parent / "prompts"


def compile_conversations(memory_root: Path) -> dict:
    """memory_root содержит daily/ и (генерируется) compiled/."""
    daily = memory_root / "daily"
    if not daily.exists():
        return {"written": []}

    files = sorted(daily.glob("*.md"))
    if not files:
        return {"written": []}

    # Объединяем содержимое всех daily
    combined = "\n\n".join(
        f"## {f.stem}\n\n{f.read_text(encoding='utf-8')}" for f in files
    )

    prompt = (PROMPTS_DIR / "conversations_concept.md").read_text(encoding="utf-8")
    try:
        sdk_out = sdk_client.generate(system=prompt, user=combined)
    except sdk_client.SDKError:
        return {"written": [], "errors": ["SDK failed"]}

    # Парсим вывод — концепты разделены ---END---
    concepts_dir = memory_root / "compiled" / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for chunk in sdk_out.split("---END---"):
        chunk = chunk.strip()
        if not chunk:
            continue
        meta, body = utils.parse_frontmatter(chunk)
        name = meta.get("name") or "concept"
        slug = utils.slugify(name)
        path = concepts_dir / f"{slug}.md"
        utils.atomic_write(path, chunk)
        written.append(str(path.name))

    # log
    log = memory_root / "compiled" / "log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{date.today().isoformat()}] conversations compile\n")
        for w in written:
            f.write(f"- {w}\n")

    return {"written": written}
