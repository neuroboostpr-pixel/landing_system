#!/usr/bin/env python3
"""Для каждого блока из structure.json → зовёт codex для генерации HTML+CSS."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_TEMPLATE = SCRIPT_DIR / "templates" / "block-generation-prompt.md"


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:40] or "x"


def call_codex(prompt_text: str, timeout: int = 120) -> str:
    """Pipe prompt to `codex exec -` and return stdout. Empty string on failure."""
    env = os.environ.copy()
    env["PATH"] = f"{env.get('HOME','')}/.local/node-current/bin:{env.get('PATH','')}"
    try:
        result = subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", "-"],
            input=prompt_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.stdout or ""
    except FileNotFoundError:
        print("ERROR: codex CLI not found in PATH", file=sys.stderr)
        return ""
    except subprocess.TimeoutExpired:
        print("WARN codex timeout", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"WARN codex error: {e}", file=sys.stderr)
        return ""


def parse_html_css(response: str):
    html_match = re.search(r"```html\s*\n(.*?)\n```", response, re.DOTALL)
    css_match = re.search(r"```css\s*\n(.*?)\n```", response, re.DOTALL)
    if not html_match or not css_match:
        return None, None
    return html_match.group(1).strip(), css_match.group(1).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", required=True)
    parser.add_argument("--screenshot", required=True)
    parser.add_argument("--niche", default="generic")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--work-dir", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.structure).read_text(encoding="utf-8"))
    blocks = data.get("blocks", [])
    page_style = data.get("page_style_summary", "")
    palette = data.get("color_palette", [])

    added = []
    library = Path(args.out)
    library.mkdir(parents=True, exist_ok=True)

    prompt_template = PROMPT_TEMPLATE.read_text(encoding="utf-8")

    host = re.sub(r"https?://(www\.)?", "", args.source_url).split("/")[0][:20]

    for i, block in enumerate(blocks):
        btype = block.get("type", "section")
        mood = block.get("style_mood", "minimal")
        desc = block.get("description", "")
        layout = block.get("layout_pattern", "stacked")

        slug = f"{btype}-{mood}-{layout}-{slugify(host)}-{i}"[:60]
        block_dir = library / btype / slug
        if block_dir.exists():
            print(f"skip {slug} (уже есть)", file=sys.stderr)
            continue
        block_dir.mkdir(parents=True, exist_ok=True)

        user_msg = (
            f"Контекст блока:\n"
            f"- type: {btype}\n"
            f"- style_mood: {mood}\n"
            f"- layout_pattern: {layout}\n"
            f"- has_animation: {block.get('has_animation', False)}\n"
            f"- description: {desc}\n"
            f"- source_page_style_summary: {page_style}\n"
            f"- source_palette: {palette}\n"
            f"- niches_suitable: {block.get('niches_suitable', [])}\n"
            f"- target_niche: {args.niche}\n"
            f"- block_id_slug: {slug}\n\n"
            f"Сгенерируй универсальный HTML+CSS блок. Output: ровно два блока кода — html и css."
        )

        full_prompt = prompt_template + "\n\n" + user_msg
        response = call_codex(full_prompt)
        html, css = parse_html_css(response)

        if not html or not css:
            print(f"warn {slug}: codex не вернул HTML+CSS, удаляю", file=sys.stderr)
            try:
                block_dir.rmdir()
            except OSError:
                pass
            continue

        (block_dir / "index.html").write_text(html + "\n", encoding="utf-8")
        (block_dir / "styles.css").write_text(css + "\n", encoding="utf-8")

        niches_lines = "\n".join(
            "  - " + n for n in (block.get("niches_suitable") or ["generic"])
        )
        meta = (
            f"id: {slug}\n"
            f"category: {btype}\n"
            f"display_name_ru: \"{(desc or btype)[:80]}\"\n"
            f"description: \"{desc}\"\n"
            f"style_mood: {mood}\n"
            f"layout_pattern: {layout}\n"
            f"ru_market: true\n"
            f"has_animation: {str(block.get('has_animation', False)).lower()}\n"
            f"niches_suitable:\n{niches_lines}\n"
            f"slots:\n"
            f"  - type: text\n"
            f"    name: heading\n"
            f"    required: true\n"
            f"imported:\n"
            f"  source_url: \"{args.source_url}\"\n"
            f"  imported_at: \"{date.today().isoformat()}\"\n"
            f"  import_method: codex-block-generation\n"
        )
        (block_dir / "meta.yaml").write_text(meta, encoding="utf-8")

        screenshot = Path(args.screenshot)
        if screenshot.exists():
            shutil.copy(screenshot, block_dir / "reference.png")

        added.append({"slug": slug, "category": btype, "path": str(block_dir)})
        print(f"ok {slug}")

    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "added-blocks.json").write_text(
        json.dumps(added, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nИмпортировано {len(added)} блоков в {library}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
