# DS-Engine v2 (экспериментальный, параллельный флоу)

> **СТАТУС: эксперимент.** НЕ подключён к боевому конвейеру landing-system.
> Живой флоу (block-composer, reference-driven, гейты, wiki-синк) НЕ тронут.
> Цель папки: обкатывать новый ДС-движок на системном уровне (под git), пока он
> не дозреет до врастания в `agents/`/`docs/standards/`/`commands/`.

## Что это

Новый способ построения дизайн-системы лендинга: агент **рисует** макет по
переносимым правилам + рецептам мода + реестру ассетов, а не подбирает блоки.

Канон обсуждения — спеки (уже в основной ветке системы):
- `docs/superpowers/specs/2026-06-22-mood-recipes-design.md`
- `docs/superpowers/specs/2026-06-22-asset-registry-design.md`

## Структура

```
experimental/ds-engine-v2/
  standards/
    _REFERENCE-ANALYSIS-LOGIC.md   ← СВОД правил: Шаги 0–5 (анализ референса) +
                                      Г1–Г8 (геометрия/декор) + П1–П4 (покрытие приёмов) +
                                      Т1–Т3 (типографика). Проектно-независимые.
  moods/<mood>/
    recipes.yaml                   ← приёмы мода (вайб), снято глазами с референса
    assets-manifest.yaml           ← реестр визуальных ассетов (пока только grooming)
    ASSETS-TODO.md                 ← авто-отчёт «что сгенерировать» (готовые промпты)
  engine/
    build_landing_3moods.py        ← генератор: ДС → composed HTML (3 мода + переключатель)
    mood_{darkmint,freshgreen,grooming}.py  ← рендерер каждого мода (своя разметка)
    gen_assets_report.py           ← manifest → ASSETS-TODO.md (отчёт для человека)
    verify_ds_asset_pack.py        ← gate-check: plan/ready проверка asset-pack
```

## Флоу (3 звена)

1. **ДС** (recipes + manifest) — характер мода + список ассетов.
2. **HTML** — `build_landing_3moods.py` рисует composed по правилам.
3. **Отчёт** — `gen_assets_report.py` → человекочитаемый список ассетов с промптами.

## Как тестировать (для коллеги)

Движок ПАРАМЕТРИЗОВАН — принимает путь к проекту-лендингу флагом `--project`.
Проект должен иметь стандартную структуру (`05_ДИЗАЙН-СИСТЕМА/moods/`,
`07_ПРОТОТИП/prototype*.yaml`, `07c_PHOTOS/`).

```bash
# из папки engine/ (или любой) — указываешь свой проект:
cd experimental/ds-engine-v2/engine
python build_landing_3moods.py --project ~/Lendings/<твой-проект>
#   → <проект>/07b_COMPOSED/composed-3moods.html  (открыть в браузере)

python gen_assets_report.py grooming --project ~/Lendings/<твой-проект>
#   → <проект>/05_ДИЗАЙН-СИСТЕМА/moods/grooming/ASSETS-TODO.md
```

Опции:
- `--prototype <имя.yaml>` — конкретный прототип (по умолчанию активный `meta.active` или `prototype-01`).
- Без `--project` движок ищет проект на уровень выше себя (работает, только если
  скопировать `engine/` внутрь `<project>/07b_COMPOSED/`).

**Требования:** Python 3 + `pyyaml` (`pip install pyyaml`).

**Что коллега увидит:** один HTML с 3 модами и переключателем снизу (примерка),
+ человекочитаемый `ASSETS-TODO.md` с готовыми промптами для генерации ассетов,
+ `asset-pack.yaml` и структуру `assets/` под preview, слои, Canvas/Canva и исходники.

**Важно про моды:** движок читает recipes/моды ИЗ ПРОЕКТА
(`<project>/05_ДИЗАЙН-СИСТЕМА/moods/`). Эталонные recipes этой ветки лежат в
`experimental/ds-engine-v2/moods/` — при необходимости скопировать их в проект.
Эталонный тест-проект (полные данные) — `d:/AI_TEAMS/Lendings/Тест/`.

## Что осталось до врастания в боевой флоу (НЕ сделано)

- assets-manifest для dark-mint и fresh-green (сейчас только grooming);
- генератор должен ставить слоты `{{decor:}}/{{icon:}}/{{bg:}}` из манифеста в HTML
  (сейчас декор инлайн, слоты манифеста в HTML не выводятся);
- подключение к `agents/block-composer.md` + `docs/standards/` + wiki-синк;
- полная автоматическая генерация Canvas/Canva-файла через подключённый плагин/редактор.

## Что уже подключено к боевым проверкам

- `07e_visuals` требует DS asset-pack plan:
  `verify_ds_asset_pack.py --mode plan`.
- `07f_composed_final` требует готовый DS asset-pack:
  `verify_ds_asset_pack.py --mode ready`.
- Канон полного пакета описан в `docs/standards/ds-asset-pack.md`.

Сам рендерер `composed-3moods.html` пока остаётся experimental, но контракт ассетов
уже используется как gate, чтобы финальная верстка не уходила без материалов.
