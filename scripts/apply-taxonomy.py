#!/usr/bin/env python3
"""B34 Фаза 1 — применить результаты классификации к meta.yaml блоков.

На вход подаётся JSON-массив результатов классификации (из workflow
b34-classify-blocks): для каждого блока category + variant + confidence + reasoning.

Скрипт:
  1. Валидирует каждый результат против taxonomy.yaml.
  2. Пишет category + variant в соответствующий meta.yaml.
  3. Генерирует migration-report.md: что куда отнесено + список low-confidence
     (требуют ручной проверки).

Использование:
  python scripts/apply-taxonomy.py --results <results.json> [--dry-run]

results.json: [{"id": "...", "folder_cat": "...", "category": "...",
                "variant": "..."|null, "confidence": "high|medium|low",
                "reasoning": "..."}, ...]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB = REPO_ROOT / "block-library"
LOADER_PATH = REPO_ROOT / "scripts" / "lib" / "taxonomy.py"


def _load_taxonomy_lib():
    spec = importlib.util.spec_from_file_location("taxonomy_lib_apply", LOADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _find_meta_path(block_id: str, folder_cat: str) -> Path | None:
    """Найти meta.yaml блока. Сначала по folder_cat, потом поиском."""
    candidate = LIB / folder_cat / block_id / "meta.yaml"
    if candidate.exists():
        return candidate
    # fallback: поиск по всем категориям
    for mp in LIB.glob(f"*/{block_id}/meta.yaml"):
        return mp
    return None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--results", required=True, help="JSON с результатами классификации")
    p.add_argument("--dry-run", action="store_true", help="не писать meta.yaml, только отчёт")
    args = p.parse_args()

    lib = _load_taxonomy_lib()
    results = json.loads(Path(args.results).read_text(encoding="utf-8"))
    # допускаем как {"results": [...]} так и просто [...]
    if isinstance(results, dict):
        results = results.get("results", [])

    applied: list[dict] = []
    invalid: list[dict] = []
    low_conf: list[dict] = []
    not_found: list[dict] = []

    for r in results:
        bid = r.get("id")
        cat = r.get("category")
        variant = r.get("variant")
        conf = r.get("confidence", "?")
        folder_cat = r.get("folder_cat", "")

        # нормализация: пустую строку → None
        if variant in ("", "null"):
            variant = None

        # валидация против taxonomy
        if not lib.valid_category(cat):
            invalid.append({**r, "_why": f"невалидная category '{cat}'"})
            continue
        if not lib.valid_variant(cat, variant):
            invalid.append({**r, "_why": f"невалидный variant '{variant}' для '{cat}'"})
            continue

        mp = _find_meta_path(bid, folder_cat)
        if mp is None:
            not_found.append(r)
            continue

        if not args.dry_run:
            meta = yaml.safe_load(mp.read_text(encoding="utf-8")) or {}
            meta["category"] = cat
            meta["variant"] = variant
            mp.write_text(
                yaml.dump(meta, default_flow_style=False, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )

        rec = {**r, "_meta": str(mp.relative_to(REPO_ROOT))}
        applied.append(rec)
        if conf == "low":
            low_conf.append(rec)

    # --- отчёт ---
    lines: list[str] = []
    lines.append("# B34 Фаза 1 — отчёт о миграции таксономии\n")
    lines.append(f"Всего результатов: {len(results)}")
    lines.append(f"Применено: {len(applied)}")
    lines.append(f"Невалидных (пропущено): {len(invalid)}")
    lines.append(f"Не найдено meta.yaml: {len(not_found)}")
    lines.append(f"Low confidence (требуют проверки): {len(low_conf)}\n")

    # распределение по category/variant
    dist: dict[str, int] = {}
    for r in applied:
        key = r["category"] + ("/" + r["variant"] if r["variant"] else "")
        dist[key] = dist.get(key, 0) + 1
    lines.append("## Распределение по (category/variant)\n")
    for k in sorted(dist):
        lines.append(f"- {k}: {dist[k]}")
    lines.append("")

    if low_conf:
        lines.append("## ⚠️ Low confidence — проверить вручную\n")
        for r in low_conf:
            v = r["variant"] or "—"
            lines.append(f"- **{r['id']}** → {r['category']}/{v}: {r.get('reasoning','')}")
        lines.append("")

    if invalid:
        lines.append("## ❌ Невалидные (НЕ применены)\n")
        for r in invalid:
            lines.append(f"- **{r.get('id')}**: {r.get('_why')} (был folder={r.get('folder_cat')})")
        lines.append("")

    if not_found:
        lines.append("## ⚠️ meta.yaml не найден\n")
        for r in not_found:
            lines.append(f"- {r.get('id')} (folder={r.get('folder_cat')})")
        lines.append("")

    report_path = LIB / "migration-report-b34.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Применено: {len(applied)}, "
          f"невалидных: {len(invalid)}, не найдено: {len(not_found)}, "
          f"low-conf: {len(low_conf)}")
    print(f"Отчёт: {report_path.relative_to(REPO_ROOT)}")
    if invalid:
        print("ВНИМАНИЕ: есть невалидные результаты — см. отчёт", file=sys.stderr)


if __name__ == "__main__":
    main()
