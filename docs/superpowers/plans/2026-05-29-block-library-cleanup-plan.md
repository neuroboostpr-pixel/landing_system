# Block Library Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Привести 190 блоков `block-library/` к единому стандарту — плейсхолдеры вместо текста, нейтральный lo-fi стиль, новая таксономия (27 типов), сквозная нумерация `тип-NNN`, удаление дублей.

**Architecture:** Три фазы. Фаза 1 — Codex чистит каждый блок в `.cleanup-staging/` (оригиналы целы). Фаза 2 — дедуп по сигнатурам + интерактивный отчёт `dedup-report.html`. Фаза 3 — удаление дублей, сквозная нумерация, пересборка `catalog.yaml`. Чистые функции (group_duplicates / renumber / build_new_structure) тестируются без Codex; Codex-вызовы мокаются.

**Tech Stack:** Python 3.10+, Codex CLI (vision/text), PyYAML, pytest. Переиспользует `check_duplicates.compute_signature`, `block-generation.md` промпт, `taxonomy.yaml`, `render-gallery.py`.

---

## Карта файлов

| Файл | Действие | Ответственность |
|---|---|---|
| `skills/block-library-management/prompts/cleanup-classify.md` | Создать | Промпт Codex: чистка + классификация по taxonomy |
| `skills/block-library-management/scripts/cleanup_lib.py` | Создать | Чистые функции: group_duplicates, renumber, build_new_structure |
| `skills/block-library-management/scripts/cleanup_blocks.py` | Создать | Оркестратор 3 фаз (вызывает Codex + cleanup_lib) |
| `skills/block-library-management/scripts/dedup_report.py` | Создать | Генератор dedup-report.html |
| `tests/block-library/test_cleanup.py` | Создать | Unit-тесты чистых функций (моки Codex) |

`compute_signature` импортируется из `skills/landing-import-blocks/scripts/check_duplicates.py` через importlib (папка с дефисом).

---

## Task 0: Git-ветка для чистки

**Files:** нет (git-операция)

- [ ] **Step 1: Создать и переключиться на ветку**

```bash
cd d:\AI_TEAMS\landing_system
git checkout -b block-library-cleanup
git branch --show-current
```
Ожидание: `block-library-cleanup`

- [ ] **Step 2: Добавить .cleanup-staging в .gitignore**

Дописать в конец `.gitignore`:
```
.cleanup-staging/
```

- [ ] **Step 3: Коммит**

```bash
git add .gitignore
git commit -m "chore(cleanup): branch + gitignore staging dir"
```

---

## Task 1: cleanup_lib.py — чистые функции дедупа и нумерации

**Files:**
- Create: `skills/block-library-management/scripts/cleanup_lib.py`
- Create: `tests/block-library/test_cleanup.py`

- [ ] **Step 1: Написать тесты**

```python
# tests/block-library/test_cleanup.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "cleanup_lib",
    Path(__file__).parents[2] / "skills" / "block-library-management" / "scripts" / "cleanup_lib.py"
)
cleanup_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cleanup_lib)

group_duplicates = cleanup_lib.group_duplicates
renumber = cleanup_lib.renumber
build_new_structure = cleanup_lib.build_new_structure


def test_group_duplicates_finds_groups():
    blocks = [
        {"old_id": "a", "signature": "hero|split|[cta,headline]|bg:false"},
        {"old_id": "b", "signature": "hero|split|[cta,headline]|bg:false"},
        {"old_id": "c", "signature": "faq|stacked|[q]|bg:false"},
    ]
    groups = group_duplicates(blocks)
    # Только группы с >1 блоком
    assert "hero|split|[cta,headline]|bg:false" in groups
    assert len(groups["hero|split|[cta,headline]|bg:false"]) == 2
    assert "faq|stacked|[q]|bg:false" not in groups  # одиночка не попадает

def test_group_duplicates_no_dupes():
    blocks = [
        {"old_id": "a", "signature": "hero|split|[h]|bg:false"},
        {"old_id": "b", "signature": "faq|stacked|[q]|bg:false"},
    ]
    assert group_duplicates(blocks) == {}

def test_renumber_sequential_by_type():
    blocks = [
        {"old_id": "trust-corp-1", "type": "stats"},
        {"old_id": "ru-stats-01", "type": "stats"},
        {"old_id": "hero-x", "type": "hero"},
    ]
    mapping = renumber(blocks)
    # ru-* первыми → ru-stats-01 = stats-001
    assert mapping["ru-stats-01"] == "stats-001"
    assert mapping["trust-corp-1"] == "stats-002"
    assert mapping["hero-x"] == "hero-001"

def test_renumber_ru_priority():
    blocks = [
        {"old_id": "zzz-block", "type": "cta"},
        {"old_id": "ru-cta-09", "type": "cta"},
    ]
    mapping = renumber(blocks)
    assert mapping["ru-cta-09"] == "cta-001"
    assert mapping["zzz-block"] == "cta-002"

def test_build_new_structure_skips_removed():
    blocks = [
        {"old_id": "a", "type": "hero", "category": "Hero", "old_path": "hero/a"},
        {"old_id": "b", "type": "hero", "category": "Hero", "old_path": "hero/b"},
    ]
    keep_list = {"removed": ["b"], "kept": ["a"]}
    actions = build_new_structure(blocks, keep_list)
    # Только 'a' остаётся, переименовывается в hero-001
    assert len(actions) == 1
    assert actions[0]["old_id"] == "a"
    assert actions[0]["new_id"] == "hero-001"
    assert actions[0]["new_path"] == "Hero/hero-001"

def test_build_new_structure_needs_manual_untouched():
    blocks = [
        {"old_id": "a", "type": "hero", "category": "Hero", "old_path": "hero/a", "status": "needs_manual"},
    ]
    keep_list = {"removed": [], "kept": ["a"]}
    actions = build_new_structure(blocks, keep_list)
    # needs_manual не переименовывается
    assert actions == []
```

- [ ] **Step 2: Запустить — убедиться что FAIL**

```
cd d:\AI_TEAMS\landing_system
python -m pytest tests/block-library/test_cleanup.py -v
```
Ожидание: FAIL — модуль не существует.

- [ ] **Step 3: Создать cleanup_lib.py**

```python
# skills/block-library-management/scripts/cleanup_lib.py
"""Чистые функции для block-library cleanup: дедуп, нумерация, план перемещений."""
from __future__ import annotations


def group_duplicates(blocks: list[dict]) -> dict[str, list[dict]]:
    """Сгруппировать блоки по signature. Вернуть только группы с >1 блоком."""
    by_sig: dict[str, list[dict]] = {}
    for b in blocks:
        sig = b.get("signature", "")
        by_sig.setdefault(sig, []).append(b)
    return {sig: lst for sig, lst in by_sig.items() if len(lst) > 1}


def _sort_key(block: dict) -> tuple:
    """ru-* блоки идут первыми (приоритет ручным), потом по old_id."""
    old_id = block.get("old_id", "")
    is_ru = 0 if old_id.startswith("ru-") else 1
    return (is_ru, old_id)


def renumber(blocks: list[dict]) -> dict[str, str]:
    """Сквозная нумерация по типу: type-001, type-002. ru-* первыми.

    Returns: {old_id: new_id}
    """
    by_type: dict[str, list[dict]] = {}
    for b in blocks:
        by_type.setdefault(b["type"], []).append(b)

    mapping: dict[str, str] = {}
    for block_type, lst in by_type.items():
        for i, b in enumerate(sorted(lst, key=_sort_key), start=1):
            mapping[b["old_id"]] = f"{block_type}-{i:03d}"
    return mapping


def build_new_structure(blocks: list[dict], keep_list: dict) -> list[dict]:
    """Построить план перемещений для оставшихся (не removed, не needs_manual) блоков.

    Returns: list of {old_id, new_id, old_path, new_path}
    """
    removed = set(keep_list.get("removed", []))
    survivors = [
        b for b in blocks
        if b["old_id"] not in removed and b.get("status") != "needs_manual"
    ]
    mapping = renumber(survivors)
    actions = []
    for b in survivors:
        new_id = mapping[b["old_id"]]
        actions.append({
            "old_id": b["old_id"],
            "new_id": new_id,
            "old_path": b["old_path"],
            "new_path": f"{b['category']}/{new_id}",
        })
    return actions
```

- [ ] **Step 4: Запустить тесты**

```
python -m pytest tests/block-library/test_cleanup.py -v
```
Ожидание: 6 PASSED.

- [ ] **Step 5: Коммит**

```bash
git add skills/block-library-management/scripts/cleanup_lib.py tests/block-library/test_cleanup.py
git commit -m "feat(cleanup): pure functions group_duplicates/renumber/build_new_structure"
```

---

## Task 2: cleanup-classify.md — промпт чистки и классификации

**Files:**
- Create: `skills/block-library-management/prompts/cleanup-classify.md`

- [ ] **Step 1: Создать промпт**

```markdown
# Role

You are a senior frontend developer cleaning up a landing-page block library. You receive ONE block's existing HTML and must produce a clean, language-agnostic, style-neutral version, plus classify it into the new taxonomy.

# CRITICAL: Placeholders only — NO real text

The template is language-agnostic. It MUST NOT contain meaningful words, sentences, or content in ANY language. Every content element contains ONLY `[SLOT: <name>]`.
- ❌ `<h1 data-slot="headline">Вы получили подарок!</h1>`
- ✅ `<h1 data-slot="headline">[SLOT: headline]</h1>`

# CRITICAL: Neutral styles only

- Colors ONLY: `#f5f5f5` (bg), `#e8e8e8` (cards), `#d0d0d0` (images/icons), `#333` (text), `#999` (buttons)
- Font: `font-family: system-ui, sans-serif`
- NO gradients, NO background-image (use `background-color:#d0d0d0`), NO decorative shadows
- Preserve ALL layout: grid columns, flex, positions, proportions

# Slot rules

Every content element: `data-slot="name"` containing only `[SLOT: name]`.
- Image: `<div data-slot="image" style="background:#d0d0d0;aspect-ratio:16/9">[SLOT: image]</div>`
- Icon: `<div data-slot="icon" style="width:48px;height:48px;background:#d0d0d0">[SLOT: icon]</div>`
- CTA: `<a data-slot="cta" style="background:#999;color:#fff;padding:12px 24px">[SLOT: cta]</a>`
- Repeated items: number them — `[SLOT: card-1-title]`, `[SLOT: card-2-title]`
- Background image: `<!-- BG PHOTO -->` + `background-color:#d0d0d0`

# Classification

Classify the block by its CONTENT (not its old name) into ONE type:

header, menu, hero, features, characteristics, about, problem-solution, process,
demo, testimonials, logos, stats, case-study, media-mentions, guarantees,
comparison, integrations, cta, banner, urgency, lead-form, pricing, faq,
gallery, team, footer, contacts

Map each type to its category:
- Navigation: header, menu
- Hero: hero
- Content: features, characteristics, about, problem-solution, process, demo
- Social Proof: testimonials, logos, stats, case-study, media-mentions
- Trust: guarantees, comparison, integrations
- Conversion: cta, banner, urgency, lead-form
- Pricing: pricing
- FAQ: faq
- Gallery: gallery, team
- Footer: footer, contacts

# Output (strict JSON, no prose, no markdown fences)

{
  "type": "<one type>",
  "category": "<matching category>",
  "layout_pattern": "split|centered|grid-2|grid-3|grid-4|stacked|bento|sidebar|cards|timeline|multi-step",
  "has_bg_image": false,
  "slots": [{"name": "headline", "type": "text"}, {"name": "image", "type": "image"}],
  "display_name_ru": "Тип: элемент + элемент",
  "clean_html": "<style>...</style><section data-block-type=\"TYPE\">...</section>"
}

display_name_ru: format "TypeLabel: element + element", slot names only, NO colors/styles.
clean_html: one <section> with inline <style>, placeholders only, neutral colors.
```

- [ ] **Step 2: Коммит**

```bash
git add skills/block-library-management/prompts/cleanup-classify.md
git commit -m "feat(cleanup): cleanup-classify Codex prompt (placeholders + taxonomy)"
```

---

## Task 3: cleanup_blocks.py — Фаза 1 (чистка через Codex)

**Files:**
- Create: `skills/block-library-management/scripts/cleanup_blocks.py`

- [ ] **Step 1: Написать тест фазы 1 (мок Codex)**

Добавить в `tests/block-library/test_cleanup.py`:

```python
import importlib.util as _ilu2
_spec2 = _ilu2.spec_from_file_location(
    "cleanup_blocks",
    Path(__file__).parents[2] / "skills" / "block-library-management" / "scripts" / "cleanup_blocks.py"
)
cleanup_blocks = _ilu2.module_from_spec(_spec2)
_spec2.loader.exec_module(cleanup_blocks)


def test_parse_codex_json_valid():
    raw = '{"type":"hero","category":"Hero","layout_pattern":"split","has_bg_image":false,"slots":[{"name":"headline","type":"text"}],"display_name_ru":"Hero: заголовок","clean_html":"<section>x</section>"}'
    result = cleanup_blocks.parse_codex_json(raw)
    assert result["type"] == "hero"
    assert result["display_name_ru"] == "Hero: заголовок"

def test_parse_codex_json_with_fence():
    raw = 'noise\n```json\n{"type":"faq","category":"FAQ","layout_pattern":"stacked","has_bg_image":false,"slots":[],"display_name_ru":"FAQ","clean_html":"<section></section>"}\n```\nmore'
    result = cleanup_blocks.parse_codex_json(raw)
    assert result["type"] == "faq"

def test_parse_codex_json_invalid_returns_none():
    assert cleanup_blocks.parse_codex_json("not json at all") is None

def test_staging_record_shape(tmp_path):
    # build_staging_record собирает запись для staging
    block_meta = {"id": "old-x"}
    codex_out = {
        "type": "hero", "category": "Hero", "layout_pattern": "split",
        "has_bg_image": False, "slots": [{"name": "h", "type": "text"}],
        "display_name_ru": "Hero: h", "clean_html": "<section></section>",
    }
    rec = cleanup_blocks.build_staging_record("hero/old-x", "old-x", codex_out)
    assert rec["old_id"] == "old-x"
    assert rec["type"] == "hero"
    assert rec["status"] == "ok"
    assert "signature" in rec
    assert rec["signature"].startswith("hero|split|")
```

- [ ] **Step 2: Запустить — убедиться что FAIL**

```
python -m pytest tests/block-library/test_cleanup.py -k codex -v
python -m pytest tests/block-library/test_cleanup.py -k staging -v
```
Ожидание: FAIL — функции не существуют.

- [ ] **Step 3: Создать cleanup_blocks.py**

```python
# skills/block-library-management/scripts/cleanup_blocks.py
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
REPO_ROOT = Path(__file__).resolve().parents[2]
STAGING = REPO_ROOT / ".cleanup-staging"
PROMPT = SCRIPT_DIR.parent / "prompts" / "cleanup-classify.md"

# compute_signature из check_duplicates (папка с дефисом → importlib)
import importlib.util as _ilu
_cd_path = REPO_ROOT / "skills" / "landing-import-blocks" / "scripts" / "check_duplicates.py"
_spec = _ilu.spec_from_file_location("cleanup_check_dup", _cd_path)
_cd = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_cd)
compute_signature = _cd.compute_signature

# чистые функции
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
    # Попробовать fenced ```json
    m = re.search(r"```json\s*\n(.*?)\n```", response, re.DOTALL)
    candidates = [m.group(1)] if m else []
    # Иначе — найти первый {...} баланс
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
    """Собрать staging-запись из вывода Codex."""
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
    """Прогнать каждый блок через Codex, сложить в staging."""
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
            continue  # idempotent — уже обработан
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
    """Дедуп + dedup-report.html."""
    blocks = [b for b in _load_staging() if b.get("status") == "ok"]
    groups = group_duplicates(blocks)
    report_path = library / "dedup-report.html"
    # импорт генератора отчёта
    _dr_path = SCRIPT_DIR / "dedup_report.py"
    _spec_dr = _ilu.spec_from_file_location("dedup_report_mod", _dr_path)
    _dr = _ilu.module_from_spec(_spec_dr)
    _spec_dr.loader.exec_module(_dr)
    _dr.render_report(groups, report_path)
    print(f"Фаза 2: {len(groups)} групп дублей. Отчёт: {report_path}")
    print("Открой отчёт, отметь что удалить, скачай keep-list.yaml, запусти фазу 3.")
    return 0


def phase3(library: Path, keep_list_path: Path) -> int:
    """Удалить дубли, перенумеровать, пересобрать."""
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
        # удалить старую папку (если путь отличается от нового)
        old_dir = library / rec["old_path"]
        if old_dir.exists() and old_dir.resolve() != new_dir.resolve():
            shutil.rmtree(old_dir)

    (library / "migration-map.yaml").write_text(
        yaml.safe_dump(migration, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    print(f"Фаза 3: перенесено {len(actions)} блоков. migration-map.yaml записан.")
    print("Теперь: пересобери catalog.yaml и gallery.html (rebuild-catalog + render-gallery).")
    return 0


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
```

- [ ] **Step 4: Запустить тесты parse/staging**

```
python -m pytest tests/block-library/test_cleanup.py -v
```
Ожидание: все PASSED (6 из Task 1 + 4 новых = 10).

- [ ] **Step 5: Коммит**

```bash
git add skills/block-library-management/scripts/cleanup_blocks.py tests/block-library/test_cleanup.py
git commit -m "feat(cleanup): cleanup_blocks orchestrator — 3 phases with Codex"
```

---

## Task 4: dedup_report.py — отчёт о дублях

**Files:**
- Create: `skills/block-library-management/scripts/dedup_report.py`

- [ ] **Step 1: Написать тест**

Добавить в `tests/block-library/test_cleanup.py`:

```python
import importlib.util as _ilu3
_spec3 = _ilu3.spec_from_file_location(
    "dedup_report",
    Path(__file__).parents[2] / "skills" / "block-library-management" / "scripts" / "dedup_report.py"
)
dedup_report = _ilu3.module_from_spec(_spec3)
_spec3.loader.exec_module(dedup_report)


def test_render_report_creates_file(tmp_path):
    groups = {
        "hero|split|[cta,headline]|bg:false": [
            {"old_id": "ru-hero-01", "display_name_ru": "Hero: A", "clean_html": "<section>A</section>"},
            {"old_id": "hero-corp-2", "display_name_ru": "Hero: B", "clean_html": "<section>B</section>"},
        ]
    }
    out = tmp_path / "dedup-report.html"
    dedup_report.render_report(groups, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "ru-hero-01" in content
    assert "hero-corp-2" in content
    assert "keep-list" in content.lower()
    # первый в группе НЕ отмечен на удаление, второй отмечен
    assert "checkbox" in content.lower()

def test_render_report_empty_groups(tmp_path):
    out = tmp_path / "dedup-report.html"
    dedup_report.render_report({}, out)
    assert out.exists()
    assert "дубл" in out.read_text(encoding="utf-8").lower()
```

- [ ] **Step 2: Запустить — FAIL**

```
python -m pytest tests/block-library/test_cleanup.py -k report -v
```

- [ ] **Step 3: Создать dedup_report.py**

```python
# skills/block-library-management/scripts/dedup_report.py
"""Генератор dedup-report.html — группы дублей с чекбоксами и keep-list экспортом."""
from __future__ import annotations
import html
import json
from pathlib import Path


def render_report(groups: dict[str, list[dict]], output: Path) -> None:
    """Сгенерировать интерактивный HTML-отчёт о дублях.

    groups: {signature: [block, ...]} — только группы с >1 блоком.
    Первый блок в группе по умолчанию НЕ отмечен на удаление.
    """
    cards = []
    for sig, blocks in groups.items():
        items = []
        for idx, b in enumerate(blocks):
            old_id = html.escape(b["old_id"])
            name = html.escape(b.get("display_name_ru", ""))
            preview = b.get("clean_html", "")
            checked = "" if idx == 0 else "checked"
            items.append(
                f'<div class="dup-item">'
                f'<label><input type="checkbox" class="rm" value="{old_id}" {checked}> '
                f'удалить <b>{old_id}</b></label>'
                f'<div class="dup-name">{name}</div>'
                f'<iframe class="dup-preview" srcdoc="{html.escape(preview, quote=True)}"></iframe>'
                f'</div>'
            )
        cards.append(
            f'<div class="dup-group"><div class="dup-sig">{html.escape(sig)}</div>'
            f'<div class="dup-items">{"".join(items)}</div></div>'
        )

    empty_note = "" if groups else "<p>Дублей не найдено 🎉</p>"

    page = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<title>Дубли блоков</title><style>
body {{ font-family: system-ui, sans-serif; background: #f0f0f0; margin: 0; padding: 24px; }}
h1 {{ font-size: 1.4rem; }}
.dup-group {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
.dup-sig {{ font-family: monospace; font-size: 12px; color: #888; margin-bottom: 12px; }}
.dup-items {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.dup-item {{ flex: 1; min-width: 280px; border: 1px solid #ddd; border-radius: 6px; padding: 10px; }}
.dup-name {{ font-size: 13px; color: #555; margin: 6px 0; }}
.dup-preview {{ width: 100%; height: 200px; border: 1px solid #eee; transform: scale(1); }}
#save {{ position: fixed; bottom: 24px; right: 24px; background: #111; color: #fff;
  border: none; padding: 14px 28px; border-radius: 8px; font-size: 15px; cursor: pointer; }}
</style></head><body>
<h1>Дубли блоков — отметь что удалить, скачай keep-list.yaml</h1>
{empty_note}
{"".join(cards)}
<button id="save">Скачать keep-list.yaml</button>
<script>
document.getElementById('save').onclick = function() {{
  const removed = [...document.querySelectorAll('.rm:checked')].map(c => c.value);
  const kept = [...document.querySelectorAll('.rm:not(:checked)')].map(c => c.value);
  const yaml = 'removed:\\n' + removed.map(r => '  - ' + r).join('\\n') +
               '\\nkept:\\n' + kept.map(k => '  - ' + k).join('\\n') + '\\n';
  const blob = new Blob([yaml], {{type: 'text/yaml'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'keep-list.yaml'; a.click();
}};
</script></body></html>"""
    output.write_text(page, encoding="utf-8")
```

- [ ] **Step 4: Запустить тесты**

```
python -m pytest tests/block-library/test_cleanup.py -v
```
Ожидание: все PASSED (12 total).

- [ ] **Step 5: Коммит**

```bash
git add skills/block-library-management/scripts/dedup_report.py tests/block-library/test_cleanup.py
git commit -m "feat(cleanup): dedup_report.py — interactive duplicate report with keep-list export"
```

---

## Task 5: catalog rebuild helper

**Files:**
- Modify: `skills/block-library-management/scripts/cleanup_blocks.py` (добавить rebuild)

- [ ] **Step 1: Написать тест rebuild_catalog**

Добавить в `tests/block-library/test_cleanup.py`:

```python
def test_rebuild_catalog_from_dirs(tmp_path):
    # Создаём минимальную структуру block-library
    lib = tmp_path / "block-library"
    block = lib / "Hero" / "hero-001"
    (block / "assets").mkdir(parents=True)
    (block / "assets" / "template.html").write_text("<section></section>", encoding="utf-8")
    import yaml as _y
    (block / "meta.yaml").write_text(_y.safe_dump({
        "id": "hero-001", "type": "hero", "category": "Hero",
        "layout_pattern": "split", "display_name_ru": "Hero: x",
        "slots": [], "signature": "hero|split|[]|bg:false",
    }, allow_unicode=True), encoding="utf-8")

    cleanup_blocks.rebuild_catalog(lib)
    catalog = _y.safe_load((lib / "catalog.yaml").read_text(encoding="utf-8"))
    assert catalog["version"] == 3
    assert len(catalog["blocks"]) == 1
    assert catalog["blocks"][0]["id"] == "hero-001"
    assert catalog["blocks"][0]["path"] == "Hero/hero-001/"
```

- [ ] **Step 2: Запустить — FAIL**

```
python -m pytest tests/block-library/test_cleanup.py -k rebuild -v
```

- [ ] **Step 3: Добавить rebuild_catalog в cleanup_blocks.py**

Дописать функцию перед `def main`:

```python
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
```

Добавить вызов в конце `phase3` (после migration-map):

```python
    rebuild_catalog(library)
```

- [ ] **Step 4: Запустить тесты**

```
python -m pytest tests/block-library/test_cleanup.py -v
```
Ожидание: все PASSED (13 total).

- [ ] **Step 5: Коммит**

```bash
git add skills/block-library-management/scripts/cleanup_blocks.py tests/block-library/test_cleanup.py
git commit -m "feat(cleanup): rebuild_catalog v3 from meta.yaml scan, called in phase3"
```

---

## Task 6: Прогон Фазы 1 (реальный Codex, чекпойнт)

**Files:** нет (запуск)

- [ ] **Step 1: Запустить фазу 1**

```
cd d:\AI_TEAMS\landing_system
python skills/block-library-management/scripts/cleanup_blocks.py --phase 1 --library block-library
```
Ожидание: для каждого блока строка `ok` / `needs_manual`, в конце сводка. `.cleanup-staging/*.json` создан.
ПРИМЕЧАНИЕ: Codex ~10-60с на блок, 190 блоков = долго. Idempotent — повторный запуск продолжает с места.

- [ ] **Step 2: Проверить staging**

```
python -c "import json,glob; recs=[json.load(open(f,encoding='utf-8')) for f in glob.glob('.cleanup-staging/*.json')]; from collections import Counter; print(Counter(r['status'] for r in recs)); print('total', len(recs))"
```
Ожидание: counter ok/needs_manual, total близко к 190.

- [ ] **Step 3: Чекпойнт-коммит**

```bash
git add -A
git commit -m "chore(cleanup): phase 1 complete — blocks cleaned to staging"
```

---

## Task 7: Прогон Фазы 2 + ручной дедуп (чекпойнт)

**Files:** нет (запуск + ручной шаг)

- [ ] **Step 1: Сгенерировать отчёт**

```
python skills/block-library-management/scripts/cleanup_blocks.py --phase 2 --library block-library
```
Ожидание: `block-library/dedup-report.html` создан, выведено число групп дублей.

- [ ] **Step 2: Ручной шаг — пользователь**

Открыть `block-library/dedup-report.html`, отметить блоки на удаление, нажать "Скачать keep-list.yaml", положить файл в корень `landing_system/`.

- [ ] **Step 3: Чекпойнт-коммит**

```bash
git add keep-list.yaml block-library/dedup-report.html
git commit -m "chore(cleanup): phase 2 — dedup decisions in keep-list.yaml"
```

---

## Task 8: Прогон Фазы 3 + финальная галерея (чекпойнт)

**Files:** нет (запуск)

- [ ] **Step 1: Запустить фазу 3**

```
python skills/block-library-management/scripts/cleanup_blocks.py --phase 3 --library block-library --keep-list keep-list.yaml
```
Ожидание: блоки перенесены в `block-library/<Category>/<type-NNN>/`, `migration-map.yaml` + `catalog.yaml` v3 записаны.

- [ ] **Step 2: Перегенерировать галерею**

```
python skills/block-library-management/scripts/render-gallery.py --library block-library --output block-library/gallery.html
```
Ожидание: gallery rendered с новым числом блоков.

- [ ] **Step 3: Проверить — открыть gallery.html, убедиться: плейсхолдеры, нейтральный стиль, новые имена type-NNN**

- [ ] **Step 4: Финальный коммит**

```bash
git add -A
git commit -m "chore(cleanup): phase 3 — blocks renumbered, new taxonomy, catalog v3, gallery rebuilt"
```

---

## Task 9: Финальный отчёт + merge решение

- [ ] **Step 1: Сводка**

```
python -c "import yaml; c=yaml.safe_load(open('block-library/catalog.yaml',encoding='utf-8')); from collections import Counter; print('Всего:', len(c['blocks'])); print(Counter(b['category'] for b in c['blocks']))"
```

- [ ] **Step 2: Отчёт по needs_manual**

```
python -c "import json,glob; m=[json.load(open(f,encoding='utf-8')) for f in glob.glob('.cleanup-staging/*.json')]; nm=[r['old_id'] for r in m if r.get('status')=='needs_manual']; print('needs_manual:', len(nm)); print('\n'.join(nm))"
```

- [ ] **Step 3: Использовать superpowers:finishing-a-development-branch** для решения по merge ветки `block-library-cleanup` в `mvp-internal-test`.
