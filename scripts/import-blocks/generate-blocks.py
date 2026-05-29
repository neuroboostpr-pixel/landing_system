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

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent

# check_duplicates лежит в skills/landing-import-blocks/scripts/ — папка с дефисом,
# поэтому грузим по пути через importlib (обычный import не сработает).
import importlib.util as _ilu

_REPO_ROOT = Path(__file__).resolve().parents[2]
_cd_path = (
    _REPO_ROOT / "skills" / "landing-import-blocks" / "scripts" / "check_duplicates.py"
)
try:
    _spec = _ilu.spec_from_file_location("gen_blocks_check_duplicates", _cd_path)
    _cd = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_cd)
    _compute_sig = _cd.compute_signature
    _HAS_SIG = True
except (FileNotFoundError, AttributeError, ImportError):
    _HAS_SIG = False

_NEW_GEN = Path(__file__).parents[2] / "skills" / "landing-import-blocks" / "prompts" / "block-generation.md"
PROMPT_TEMPLATE = _NEW_GEN if _NEW_GEN.exists() else SCRIPT_DIR / "templates" / "block-generation-prompt.md"


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:40] or "x"


def _find_codex() -> str | None:
    """Locate the codex CLI cross-platform. Returns the executable path or None."""
    import shutil
    # shutil.which honours PATHEXT on Windows (.CMD/.EXE) and POSIX on *nix.
    found = shutil.which("codex")
    if found:
        return found
    # Common explicit locations (Linux node-current, Windows npm global).
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE", "")
    appdata = os.environ.get("APPDATA", "")
    for c in (
        f"{home}/.local/node-current/bin/codex",
        f"{home}/.local/bin/codex",
        f"{appdata}\\npm\\codex.CMD" if appdata else "",
        f"{appdata}\\npm\\codex.cmd" if appdata else "",
    ):
        if c and Path(c).exists():
            return c
    return None


def call_codex(prompt_text: str, timeout: int = 120) -> str:
    """Pipe prompt to `codex exec -` and return its output. Empty string on failure.

    ВАЖНО: codex CLI (v0.12x на Windows) пишет баннер сессии И сам ответ модели
    в STDERR, а в STDOUT кладёт только token-count. Поэтому склеиваем оба потока —
    parse_html_css всё равно ищет ```html-fence внутри.
    """
    env = os.environ.copy()
    env["PATH"] = f"{env.get('HOME','')}/.local/node-current/bin{os.pathsep}{env.get('PATH','')}"
    codex_bin = _find_codex()
    if not codex_bin:
        print("ERROR: codex CLI not found in PATH", file=sys.stderr)
        return ""
    try:
        result = subprocess.run(
            [codex_bin, "exec", "--skip-git-repo-check", "-"],
            input=prompt_text,
            capture_output=True,
            text=True,
            # На Windows text=True по умолчанию кодирует stdin в cp1251, и codex
            # отвергает кириллицу как "input is not valid UTF-8". Форсим UTF-8.
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        # Ответ модели может прийти в stdout ИЛИ в stderr (зависит от версии CLI
        # и платформы) — объединяем, чтобы парсер нашёл fence в любом случае.
        return (result.stdout or "") + "\n" + (result.stderr or "")
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
    """Извлечь HTML и CSS из ответа codex.

    Поддерживает два формата:
    1. Два отдельных fence — ```html ... ``` и ```css ... ``` (старый промпт).
    2. Один ```html fence с inline <style> внутри (новый block-generation.md).
       В этом случае css="" — стили уже внутри html.

    Возвращает (html, css) или (None, None) если html-fence не найден.

    ВАЖНО: при `codex exec` echo-ится весь промпт (включая пример fence из
    block-generation.md), и только ПОСЛЕ маркера `\ncodex\n` идёт реальный ответ
    модели. Поэтому если маркер есть — парсим только хвост после него, чтобы не
    подхватить пример из промпта.
    """
    marker_idx = response.rfind("\ncodex\n")
    if marker_idx != -1:
        response = response[marker_idx + len("\ncodex\n"):]
    html_match = re.search(r"```html\s*\n(.*?)\n```", response, re.DOTALL)
    css_match = re.search(r"```css\s*\n(.*?)\n```", response, re.DOTALL)
    if html_match:
        html = html_match.group(1).strip()
        css = css_match.group(1).strip() if css_match else ""
        return html, css
    if css_match:
        # Только css — без html толку нет.
        return None, None
    return None, None


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
        category = block.get("category", btype)

        # Bug 1: если оркестратор уже вычислил _id (вида hero-001) — используем его.
        # Иначе fallback на старую логику из имени host'а.
        slug = block.get("_id") or f"{btype}-{mood}-{layout}-{slugify(host)}-{i}"[:60]
        block_dir = library / btype / slug
        if block_dir.exists():
            print(f"skip {slug} (уже есть)", file=sys.stderr)
            continue
        block_dir.mkdir(parents=True, exist_ok=True)

        slots = block.get("slots", []) or []

        user_msg = (
            f"Контекст блока:\n"
            f"- type: {btype}\n"
            f"- style_mood: {mood}\n"
            f"- layout_pattern: {layout}\n"
            f"- has_animation: {block.get('has_animation', False)}\n"
            f"- has_bg_image: {block.get('has_bg_image', False)}\n"
            f"- slots: {slots}\n"
            f"- description: {desc}\n"
            f"- source_page_style_summary: {page_style}\n"
            f"- source_palette: {palette}\n"
            f"- niches_suitable: {block.get('niches_suitable', [])}\n"
            f"- target_niche: {args.niche}\n"
            f"- block_id_slug: {slug}\n\n"
            f"Сгенерируй один HTML-блок с inline <style>. "
            f"Output: ровно один ```html fence (стили уже внутри <style>)."
        )

        full_prompt = prompt_template + "\n\n" + user_msg
        response = call_codex(full_prompt)
        html, css = parse_html_css(response)

        if not html:
            print(f"warn {slug}: codex не вернул HTML, удаляю", file=sys.stderr)
            try:
                block_dir.rmdir()
            except OSError:
                pass
            continue

        # Новый формат: assets/template.html (то что ждут block-loader.py и
        # render-gallery.py). Стили inline внутри html. Если codex всё же отдал
        # отдельный css-fence — инлайним его в <style> перед </head>/в начало.
        if css:
            style_tag = f"<style>\n{css}\n</style>"
            if "</head>" in html:
                html = html.replace("</head>", style_tag + "\n</head>", 1)
            else:
                html = style_tag + "\n" + html

        assets_dir = block_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / "template.html").write_text(html + "\n", encoding="utf-8")

        sig = _compute_sig(block) if _HAS_SIG else ""
        display_name_ru = (block.get("display_name_ru", "") or (desc or btype))[:80]
        # Строим dict и сериализуем через yaml.safe_dump — это корректно
        # экранирует пути с backslash (source_url на Windows) и любой Unicode.
        # Ручной f-string + двойные кавычки ломали YAML (\U → escape sequence).
        meta_dict = {
            "id": slug,
            "type": btype,
            "category": category,
            "display_name_ru": display_name_ru,
            "description": desc,
            "layout_pattern": layout,
            "has_bg_image": bool(block.get("has_bg_image", False)),
            "signature": sig,
            "style_mood": mood,
            "ru_market": True,
            "has_animation": bool(block.get("has_animation", False)),
            "niches_suitable": block.get("niches_suitable") or ["generic"],
            "slots": [
                {k: v for k, v in s.items() if k in ("type", "name", "required", "max_chars", "default_text")}
                for s in slots
            ] or [{"type": "text", "name": "heading", "required": True}],
            "source": "import",
            "source_url": str(args.source_url),
            "created": date.today().isoformat(),
        }
        (block_dir / "meta.yaml").write_text(
            yaml.safe_dump(meta_dict, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

        screenshot = Path(args.screenshot)
        if screenshot.exists():
            shutil.copy(screenshot, block_dir / "reference.png")

        added.append({
            "slug": slug,
            "path": str(block_dir),
            "category": category,
            "type": btype,
            "layout_pattern": layout,
            "signature": sig,
            "display_name_ru": display_name_ru[:80],
        })
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
