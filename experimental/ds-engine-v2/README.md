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
```

## Флоу (3 звена)

1. **ДС** (recipes + manifest) — характер мода + список ассетов.
2. **HTML** — `build_landing_3moods.py` рисует composed по правилам.
3. **Отчёт** — `gen_assets_report.py` → человекочитаемый список ассетов с промптами.

## Как тестировать СЕЙЧАС

Движок написан под структуру **проекта-лендинга** (читает `../07_ПРОТОТИП/`,
`../05_ДИЗАЙН-СИСТЕМА/moods/`, `../07c_PHOTOS/`). Поэтому обкатка пока идёт в
тест-проекте `d:/AI_TEAMS/Lendings/Тест/` — там полная структура и реальные данные.
Эта папка — **снапшот** артефактов под версионирование и системный обзор.

Запуск в тест-проекте:
```bash
cd <project>/07b_COMPOSED
python build_landing_3moods.py     # → composed-3moods.html
python gen_assets_report.py grooming  # → moods/grooming/ASSETS-TODO.md
```

## Что осталось до врастания в боевой флоу (НЕ сделано)

- параметризовать движок (убрать хардкод путей проекта `Тест`) → принимать project-path;
- assets-manifest для dark-mint и fresh-green (сейчас только grooming);
- генератор должен ставить слоты `{{decor:}}/{{icon:}}/{{bg:}}` из манифеста в HTML
  (сейчас декор инлайн, слоты манифеста в HTML не выводятся);
- подключение к `agents/block-composer.md` + `docs/standards/` + wiki-синк;
- перенос правил в `docs/standards/` каноном системы.

Пока всё это не сделано — флоу остаётся в `experimental/`, боевой не затрагивается.
