"""Запросы к wiki из CLI.

Использование:
  python -m scripts.wiki.query "что делает landing-orchestrator"
  python -m scripts.wiki.query "..." --project=dubai-avto-liza
  python -m scripts.wiki.query "..." --file-back  # сохраняет ответ в memory/qa/
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from scripts.wiki import config, sdk_client, utils

PROMPTS_DIR = Path(__file__).parent / "prompts"
MAX_INDEX_CHARS = 6000
MAX_CONCEPT_CHARS = 4000


def _gather_indexes(wiki_dirs: list[Path]) -> str:
    parts = []
    for w in wiki_dirs:
        idx = w / "index.md"
        if idx.exists():
            text = idx.read_text(encoding="utf-8")
            if len(text) > MAX_INDEX_CHARS:
                text = text[:MAX_INDEX_CHARS] + "\n[...обрезано]"
            parts.append(f"# Index of {w}\n\n{text}")
    return "\n\n---\n\n".join(parts)


def ask(wiki_dirs: list[Path], question: str) -> str:
    """Главная функция."""
    indexes = _gather_indexes(wiki_dirs)
    user = f"{indexes}\n\n---\n\n**Вопрос:** {question}"
    prompt = (PROMPTS_DIR / "query.md").read_text(encoding="utf-8")
    try:
        return sdk_client.generate(system=prompt, user=user)
    except sdk_client.SDKError as e:
        return f"_(ошибка SDK: {e})_"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Вопрос к wiki")
    parser.add_argument("--project", help="Slug проекта (включит его wiki + memory)")
    parser.add_argument("--file-back", action="store_true", help="Сохранить ответ в memory/qa/")
    args = parser.parse_args()

    from scripts.lib.paths import project_dir

    wiki_dirs = [config.WIKI_DIR]
    if args.project:
        project_root = project_dir(args.project)
        if (project_root / "wiki").exists():
            wiki_dirs.append(project_root / "wiki")
        if (project_root / "memory" / "compiled").exists():
            wiki_dirs.append(project_root / "memory" / "compiled")

    answer = ask(wiki_dirs=wiki_dirs, question=args.question)
    print(answer)

    if args.file_back and args.project:
        qa_dir = project_dir(args.project) / "memory" / "compiled" / "qa"
        qa_dir.mkdir(parents=True, exist_ok=True)
        slug = utils.slugify(args.question)[:60]
        out = qa_dir / f"{date.today().isoformat()}-{slug}.md"
        utils.atomic_write(
            out,
            f"# {args.question}\n\n{answer}\n",
        )
        print(f"\n💾 Сохранено: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
