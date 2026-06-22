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
ASSETS_DIR = MOODS / mood / "assets"
if not MAN.exists():
    sys.exit(f"[ОШИБКА] нет {MAN}\nУкажи проект: python gen_assets_report.py {mood} --project <путь>")

d = yaml.safe_load(MAN.read_text(encoding="utf-8"))
assets = d["assets"]
togen  = d.get("to_generate", [])

# индекс briefs по id
by_id = {a["id"]: a for a in assets}

def _slot_category(slot):
    s = str(slot or "").strip("{}")
    if ":" in s:
        return s.split(":", 1)[0]
    return "misc"

def _ext_for_format(fmt):
    f = str(fmt or "").lower()
    if "svg" in f:
        return "svg"
    if "jpg" in f or "jpeg" in f:
        return "jpg"
    if "ico" in f:
        return "png"
    if "png" in f or "фото" in f or "photo" in f:
        return "png"
    return "dat"

def _expected_path(asset):
    if "css" in str(asset.get("формат", "")).lower():
        return None
    category = _slot_category(asset.get("слот"))
    if category == "figure":
        category = "figures"
    elif category == "photo":
        category = "photos"
    elif category == "icon":
        category = "icons"
    elif category == "bg":
        category = "bg"
    elif category == "brand":
        category = "brand"
    elif category == "decor":
        category = "decor"
    else:
        category = "misc"
    return f"assets/{category}/{asset['id']}.{_ext_for_format(asset.get('формат'))}"

def _ensure_asset_dirs():
    for sub in ("bg", "brand", "canvas", "decor", "figures", "icons", "layers", "misc", "photos", "previews"):
        (ASSETS_DIR / sub).mkdir(parents=True, exist_ok=True)

def _write_support_files():
    prompts_lines = [f"# Prompts — {mood}", ""]
    for item in togen:
        asset = by_id.get(item["id"], {})
        prompt = " ".join(str(asset.get("промпт", "")).split())
        if not prompt:
            continue
        prompts_lines.extend([f"## {item['id']}", "", prompt, ""])
    (ASSETS_DIR / "prompts.md").write_text("\n".join(prompts_lines), encoding="utf-8")

    rules = f"""# Source Rules — {mood}

1. Клиентские исходники не перерисовывать и не менять по смыслу: человек, товар, техника, объект или место должны оставаться узнаваемыми.
2. Разрешены только обработка под лендинг, кадрирование, маски, свет/контраст, удаление фона, композиционная раскладка и подготовка mobile-версий.
3. Если на входе есть реальный человек или реальный объект, AI-сцены используются только как окружение/декор, а не как замена исходника.
4. Для каждого hero/CTA/ключевого блока нужен preview с реальным текстом из прототипа на desktop и mobile. Если текст плохо читается, ассет не готов.
5. SVG не должен иметь вшитый бренд-цвет, если его можно покрасить CSS-токеном. Цвет задаёт верстка через var(--lp-*).
"""
    (ASSETS_DIR / "source-rules.md").write_text(rules, encoding="utf-8")

    readme = f"""# Assets — {mood}

Эта папка — рабочий пакет для верстки. Сюда кладутся финальные файлы после генерации
через Canvas/Canva/другой редактор: preview desktop/mobile, слои, экспорт Canvas/Canva,
иконки, декор, фоны и исходные правила.
"""
    (ASSETS_DIR / "README.md").write_text(readme, encoding="utf-8")

def _write_pack_yaml():
    pack = {
        "meta": {
            "mood": mood,
            "source_manifest": str(MAN.relative_to(ROOT)),
            "status": "planned",
        },
        "required_delivery": {
            "preview_desktop": "assets/previews/preview-desktop.png",
            "preview_mobile": "assets/previews/preview-mobile.png",
            "layers": "assets/layers/layers.svg",
            "canvas_file": "assets/canvas/canvas-file.md",
            "prompts": "assets/prompts.md",
            "source_rules": "assets/source-rules.md",
        },
        "assets": [],
    }
    for asset in assets:
        expected = _expected_path(asset)
        pack["assets"].append({
            "id": asset["id"],
            "required": asset.get("нужен"),
            "slot": asset.get("слот"),
            "format": asset.get("формат"),
            "status": asset.get("статус"),
            "expected_path": expected,
        })
    (MOODS / mood / "asset-pack.yaml").write_text(
        yaml.safe_dump(pack, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

_ensure_asset_dirs()
_write_support_files()
_write_pack_yaml()

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

W("## Полный пакет для верстки")
W("")
W("Перед финальным composed и WordPress-сборкой в mood-папке должен быть не только список промптов, а готовый пакет файлов:")
W("")
W("- `assets/previews/preview-desktop.png` — desktop preview с реальным текстом из прототипа")
W("- `assets/previews/preview-mobile.png` — mobile preview с тем же реальным текстом, без наложений и мелкого нечитаемого текста")
W("- `assets/layers/layers.svg` или `assets/layers/layers.json` — вектор/слои, чтобы верстка могла разложить элементы")
W("- `assets/canvas/canvas-file.*` — Canvas/Canva-файл или экспорт/ссылка на него")
W("- `assets/prompts.md` — все промпты, по которым генерировались ассеты")
W("- `assets/source-rules.md` — правила обработки исходников: не менять человека/объект/товар, только адаптировать под стиль лендинга")
W("- `asset-pack.yaml` — машинный список ожидаемых файлов для проверки")
W("")
W("Жёсткое правило: если preview с реальным текстом плохо читается на desktop или mobile, ассет не считается готовым.")
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
        expected = _expected_path(a) if a else None
        target = expected or "CSS/token, отдельный файл не нужен"
        W(f"- **Слот в HTML:** `{a.get('слот','—')}`  ·  **Кладётся в:** `{target}`")
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
