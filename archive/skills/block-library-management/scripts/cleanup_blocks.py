"""Block library cleanup orchestrator — 3 phases.

Usage:
    python cleanup_blocks.py --phase 1 --library block-library
    python cleanup_blocks.py --phase 2 --library block-library
    python cleanup_blocks.py --phase 3 --library block-library --keep-list keep-list.yaml
"""
from __future__ import annotations
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
REPO_ROOT = Path(__file__).resolve().parents[3]
STAGING = REPO_ROOT / ".cleanup-staging"
PROMPT = SCRIPT_DIR.parent / "prompts" / "cleanup-classify.md"

import importlib.util as _ilu
_cd_path = REPO_ROOT / "skills" / "landing-import-blocks" / "scripts" / "check_duplicates.py"
_spec = _ilu.spec_from_file_location("cleanup_check_dup", _cd_path)
_cd = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_cd)
compute_signature = _cd.compute_signature

_cl_path = SCRIPT_DIR / "cleanup_lib.py"
_spec_cl = _ilu.spec_from_file_location("cleanup_lib_mod", _cl_path)
_cl = _ilu.module_from_spec(_spec_cl)
_spec_cl.loader.exec_module(_cl)
group_duplicates = _cl.group_duplicates
build_new_structure = _cl.build_new_structure


def _find_codex() -> str | None:
    found = shutil.which("codex")
    if found:
        return found
    appdata = os.environ.get("APPDATA", "")
    for c in (f"{appdata}\\npm\\codex.CMD", f"{appdata}\\npm\\codex.cmd"):
        if c and Path(c).exists():
            return c
    return None


def call_codex(prompt_text: str, timeout: int = 180) -> str:
    codex_bin = _find_codex()
    if not codex_bin:
        return ""
    try:
        result = subprocess.run(
            [codex_bin, "exec", "--skip-git-repo-check", "-"],
            input=prompt_text, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        return (result.stdout or "") + "\n" + (result.stderr or "")
    except Exception:
        return ""


def parse_codex_json(response: str) -> dict | None:
    """Извлечь JSON из ответа Codex (с fence или без)."""
    m = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
    candidates = [m.group(1)] if m else []
    if not candidates:
        start = response.find("{")
        if start != -1:
            depth = 0
            for i in range(start, len(response)):
                if response[i] == "{":
                    depth += 1
                elif response[i] == "}":
                    depth -= 1
                    if depth == 0:
                        candidates.append(response[start:i + 1])
                        break
    for c in candidates:
        try:
            obj = json.loads(c)
            if isinstance(obj, dict) and "type" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    return None


def build_staging_record(old_path: str, old_id: str, codex_out: dict) -> dict:
    block = {
        "type": codex_out.get("type", "unknown"),
        "layout_pattern": codex_out.get("layout_pattern", "stacked"),
        "slots": codex_out.get("slots", []),
        "has_bg_image": codex_out.get("has_bg_image", False),
    }
    return {
        "old_path": old_path,
        "old_id": old_id,
        "type": block["type"],
        "category": codex_out.get("category", ""),
        "layout_pattern": block["layout_pattern"],
        "slots": block["slots"],
        "has_bg_image": block["has_bg_image"],
        "display_name_ru": codex_out.get("display_name_ru", ""),
        "clean_html": codex_out.get("clean_html", ""),
        "signature": compute_signature(block),
        "status": "ok",
        "source": codex_out.get("source", "cleaned"),
    }


def phase1(library: Path) -> int:
    STAGING.mkdir(exist_ok=True)
    prompt_base = PROMPT.read_text(encoding="utf-8")
    catalog = yaml.safe_load((library / "catalog.yaml").read_text(encoding="utf-8"))
    blocks = catalog.get("blocks", [])
    ok = failed = 0
    for b in blocks:
        old_id = b["id"]
        old_path = b.get("path", "").rstrip("/")
        staging_file = STAGING / f"{old_id}.json"
        if staging_file.exists():
            continue
        tmpl = library / old_path / "assets" / "template.html"
        if not tmpl.exists():
            tmpl = library / old_path / "template.html"
        html = tmpl.read_text(encoding="utf-8") if tmpl.exists() else ""
        full = prompt_base + "\n\n# Block HTML\n\n```html\n" + html + "\n```"
        codex_out = parse_codex_json(call_codex(full))
        if codex_out:
            rec = build_staging_record(old_path, old_id, codex_out)
            ok += 1
        else:
            rec = {"old_path": old_path, "old_id": old_id, "status": "needs_manual"}
            failed += 1
        staging_file.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {rec['status']:12} {old_id}")
    print(f"\nФаза 1 готова: {ok} ok, {failed} needs_manual. Staging: {STAGING}")
    return 0


def _load_staging() -> list[dict]:
    return [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted(STAGING.glob("*.json"))
    ]


def phase2(library: Path) -> int:
    blocks = [b for b in _load_staging() if b.get("status") == "ok"]
    groups = group_duplicates(blocks)
    report_path = library / "dedup-report.html"
    _dr_path = SCRIPT_DIR / "dedup_report.py"
    _spec_dr = _ilu.spec_from_file_location("dedup_report_mod", _dr_path)
    _dr = _ilu.module_from_spec(_spec_dr)
    _spec_dr.loader.exec_module(_dr)
    _dr.render_report(groups, report_path)
    print(f"Фаза 2: {len(groups)} групп дублей. Отчёт: {report_path}")
    print("Открой отчёт, отметь что удалить, скачай keep-list.yaml, запусти фазу 3.")
    return 0


def phase3(library: Path, keep_list_path: Path) -> int:
    blocks = _load_staging()
    keep_list = yaml.safe_load(keep_list_path.read_text(encoding="utf-8"))
    actions = build_new_structure(blocks, keep_list)

    by_id = {b["old_id"]: b for b in blocks}
    migration = {}
    for act in actions:
        rec = by_id[act["old_id"]]
        new_dir = library / act["new_path"]
        (new_dir / "assets").mkdir(parents=True, exist_ok=True)
        (new_dir / "assets" / "template.html").write_text(rec["clean_html"], encoding="utf-8")
        meta = {
            "id": act["new_id"],
            "type": rec["type"],
            "category": rec["category"],
            "layout_pattern": rec["layout_pattern"],
            "display_name_ru": rec["display_name_ru"],
            "slots": rec["slots"],
            "has_bg_image": rec["has_bg_image"],
            "signature": rec["signature"],
            "source": "cleaned",
            "created": str(date.today()),
        }
        (new_dir / "meta.yaml").write_text(
            yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        migration[act["old_id"]] = act["new_id"]
        old_dir = library / rec["old_path"]
        if old_dir.exists() and old_dir.resolve() != new_dir.resolve():
            shutil.rmtree(old_dir)

    (library / "migration-map.yaml").write_text(
        yaml.safe_dump(migration, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"Фаза 3: перенесено {len(actions)} блоков. migration-map.yaml записан.")
    print("Теперь: пересобери catalog.yaml и gallery.html.")
    rebuild_catalog(library)
    return 0


def rebuild_catalog(library: Path) -> None:
    """Пересобрать catalog.yaml (v3) сканированием всех meta.yaml."""
    blocks = []
    for meta_file in sorted(library.glob("*/*/meta.yaml")):
        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
        rel = meta_file.parent.relative_to(library).as_posix()
        blocks.append({
            "id": meta.get("id", ""),
            "path": rel + "/",
            "category": meta.get("category", ""),
            "type": meta.get("type", ""),
            "layout_pattern": meta.get("layout_pattern", ""),
            "signature": meta.get("signature", ""),
            "display_name_ru": meta.get("display_name_ru", ""),
        })
    catalog = {"version": 3, "updated": str(date.today()), "blocks": blocks}
    (library / "catalog.yaml").write_text(
        yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"catalog.yaml пересобран: {len(blocks)} блоков")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phase", type=int, required=True, choices=[1, 2, 3])
    p.add_argument("--library", required=True)
    p.add_argument("--keep-list", default="keep-list.yaml")
    args = p.parse_args(argv)
    lib = Path(args.library).resolve()
    if args.phase == 1:
        return phase1(lib)
    if args.phase == 2:
        return phase2(lib)
    return phase3(lib, Path(args.keep_list))


if __name__ == "__main__":
    sys.exit(main())
