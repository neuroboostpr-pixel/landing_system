#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отчёт по ассетам: читает moods/<mood>/assets-manifest.yaml → человекочитаемый
ASSETS-TODO.md — что нужно сгенерировать/положить, сгруппировано по режиму.

Третье звено флоу: ДС (рецепт+манифест) → HTML → ОТЧЁТ для человека.
Запуск:  python gen_assets_report.py <mood>     (по умолчанию grooming)
"""
import sys, pathlib, yaml

import argparse
ap = argparse.ArgumentParser(description="manifest → ASSETS-TODO.md (отчёт для человека)")
ap.add_argument("mood", nargs="?", default="grooming", help="мод (grooming/dark-mint/fresh-green)")
ap.add_argument("--project", help="путь к проекту-лендингу (иначе автопоиск на уровень выше)")
args = ap.parse_args()

ROOT  = (pathlib.Path(args.project).expanduser().resolve()
         if args.project else pathlib.Path(__file__).resolve().parents[1])
MOODS = ROOT / "05_ДИЗАЙН-СИСТЕМА" / "moods"
mood  = args.mood
MAN   = MOODS / mood / "assets-manifest.yaml"
OUT   = MOODS / mood / "ASSETS-TODO.md"
if not MAN.exists():
    sys.exit(f"[ОШИБКА] нет {MAN}\nУкажи проект: python gen_assets_report.py {mood} --project <путь>")

d = yaml.safe_load(MAN.read_text(encoding="utf-8"))
assets = d["assets"]
togen  = d.get("to_generate", [])

# индекс briefs по id
by_id = {a["id"]: a for a in assets}

# статистика
total   = len(assets)
ready   = [a for a in assets if str(a.get("статус","")).startswith("готов")]
stub    = [a for a in assets if str(a.get("статус","")).startswith("заглушка")]

REZHIM_LABEL = {
    "single":       "🔹 По одному (single) — каждый файл свой бриф",
    "batch-sheet":  "🔸 Пакет-лист (batch-sheet) — N на одном листе → НАРЕЗАТЬ",
    "batch-series": "🔹 Серия (batch-series) — N кадров в едином стиле, без нарезки",
}

lines = []
W = lines.append
W(f"# Ассеты для генерации — мод «{mood}»")
W("")
W(f"> Авто-отчёт из `assets-manifest.yaml`. Берёшь **ПРОМПТ**, вставляешь в генератор,")
W(f"> кладёшь файл в `moods/{mood}/assets/`. Плейсхолдеры `{{субъект из ниши}}` / `{{фичи}}`")
W(f"> подставляются из `market-profile.md` проекта. Цвет SVG задаёт CSS-токен — в промпте его нет.")
W("")
W(f"**Итого ассетов:** {total}  ·  **готово (система):** {len(ready)}  ·  **нужно сгенерировать:** {len(stub)}")
W("")

# группировка нужного к генерации по режиму
groups = {"batch-sheet": [], "batch-series": [], "single": []}
for item in togen:
    a = by_id.get(item["id"], {})
    rez = item.get("режим") or a.get("режим") or "single"
    groups.setdefault(rez, []).append((item, a))

for rez in ("batch-sheet", "batch-series", "single"):
    items = groups.get(rez, [])
    if not items: continue
    W(f"## {REZHIM_LABEL.get(rez, rez)}")
    W("")
    for item, a in items:
        opt = "  *(опционально)*" if item.get("опц") or a.get("нужен")=="optional" else ""
        n   = f"  · {item['n']}" if item.get("n") else ""
        W(f"### {a.get('id','?')}{opt}")
        W(f"- **Что:** {a.get('роль_где','—')}")
        W(f"- **Формат:** {item.get('формат', a.get('формат','—'))}  ·  **Размер:** {a.get('размеры','—')}{n}")
        W(f"- **Слот в HTML:** `{a.get('слот','—')}`  ·  **Кладётся в:** `assets/`")
        prm = ' '.join(str(a.get('промпт','')).split())
        if prm:
            W("")
            W("**🟢 ПРОМПТ (копировать в генератор):**")
            W("```")
            W(prm)
            W("```")
        else:
            W(f"- *(промпт не задан — см. бриф: {' '.join(str(a.get('бриф','')).split())})*")
        W("")
    W("")

# что система уже закрыла (для полноты картины)
W("## ✅ Уже готово системой (CSS/токены — генерить не нужно)")
W("")
for a in ready:
    W(f"- **{a['id']}** — {a.get('роль_где','')}  (`{a.get('слот','')}`)")
W("")

# памятка по нарезке/режимам
W("---")
W("**Как генерировать:**")
W("- 🔸 batch-sheet — один запрос на лист (иконки/глифы), потом нарезать на файлы по слотам.")
W("- 🔹 batch-series — один стиль-бриф на серию (фигуры/фото/росчерки), кадры по отдельности.")
W("- 🔹 single — уникальный ассет (фон-сцена, лого, фавикон), свой бриф.")
W("- Готовые файлы класть в `assets/{decor,bg,figures,icons,brand}/`, статус в манифесте → `готов`.")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"OK → {OUT}")
print(f"   ассетов: {total} | готово: {len(ready)} | к генерации: {len(stub)}")
print(f"   batch-sheet: {len(groups['batch-sheet'])} | batch-series: {len(groups['batch-series'])} | single: {len(groups['single'])}")
