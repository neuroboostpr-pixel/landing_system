---
type: stage
name: pr-c-visual-generation-plan
sources: ["docs/superpowers/plans/2026-05-13-visual-generation-plan.md"]
updated: 2026-05-18
triggers: []
stage: "07d"
uses:
  - visual-curator
  - icon-generator
  - infographic-builder
  - visual-generation
  - landing-visuals
  - block-composition
  - block-composer
  - landing-compose
tags:
  - pr-c
  - icons
  - infographics
  - codex
  - image-gen
  - stage-07d
---

# PR-C Visual Generation — план реализации этапа 07d

## Что делает

Строит конвейер AI-генерации иконок и инфографики для лендинга. Находит все слоты `data-slot-type="icon"` и `data-slot-type="infographic"` в `composed.html`, генерирует PNG через codex `image_gen`, подставляет их обратно в HTML. Параметры берёт из `tokens.json` (цвета, стиль) и `market-profile.md` (ниша). Повторные запуски используют хэш-кэш — codex не вызывается второй раз для тех же слотов.

## Когда вызывать / в каком этапе

**Этап 07d.** Запускается вручную командой `/landing-visuals` после:
1. Этап 05 (`05_design`) утверждён — `tokens.json` должен существовать.
2. Существует `07b_COMPOSED/composed.html` (создаётся на этапе PR-A командой `/landing-compose`).

Интеграция в `landing-orchestrator` запланирована отдельным PR-D.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — HTML с незаполненными слотами `[SLOT: ...]`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвет акцента, визуальный стиль, стиль иконок
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ниша (нужна для промпта)
- `block-library/` иконки через `icons.csv`, инфографика через 90 JSON-шаблонов OpenDesign

**Выход (в `07d_VISUALS/`):**
- `icons/<slot-name>.png` — сгенерённые иконки
- `infographics/<slot-name>.png` — сгенерённые инфографики
- `.cache/<hash>.png` — кэш по `hash(hint+style+brand_color+niche)`
- `_slots.yaml` — найденные слоты
- `prompts.yaml` — лог промптов с attribution (для OpenDesign CC-BY-4.0)
- `STATE.yaml` — статусы трёх стадий: scan / generate / inject
- Обновлённый `07b_COMPOSED/composed.html` — placeholders заменены на `<img>`

## Архитектура (12 задач плана)

| Задача | Артефакт | Назначение |
|--------|----------|------------|
| 1 | `slot-scanner.py` | Парсит `composed.html`, выдаёт YAML-список icon/infographic слотов |
| 2 | `prompt-picker.py` | Waterfall: `icons.csv` → generic (иконки); OpenDesign JSON → generic (инфографика) |
| 3 | `visual-cache.py` | Хэш-кэш skip-if-exists, `FORCE=1` обходит |
| 4 | `SKILL.md` + 2 шаблона | Скаффолд скилла, `icon-prompt.md`, `infographic-prompt.md` |
| 5 | `codex-generate-icon.sh` / `-infographic.sh` | Bash-обёртки для codex CLI (паттерн paralaximus snapshot+comm+copy) |
| 6 | 3 агент-доки | `visual-curator`, `icon-generator`, `infographic-builder` |
| 7 | `inject-content.py` расширение | Ветки icon/infographic; параметр `--visuals-dir`; обратная совместимость с PR-A и PR-B |
| 8 | `commands/landing-visuals.md` | Слеш-команда с флагами `--type`, `--force`, `--slot` |
| 9 | 2 новых блока | `ru-features-XX-kpi-metrics` и `ru-stats-XX-growth-chart` со слотами `type: infographic` |
| 10 | `template/07d_VISUALS/README.md` | Объяснение папки маркетологу (русский язык) |
| 11 | `test-pipeline.sh` | PR-C стадия в smoke-тесте |
| 12 | `THIRD_PARTY_NOTICES.md` + `CLAUDE.md` | Attribution для OpenDesign промптов |

**Технический стек:** Python 3.10+, BeautifulSoup4, PyYAML, Pillow; bash + bats; pytest; codex CLI v0.125+. Новых внешних зависимостей нет.

## Связанные концепты

- [[visual-curator]] — оркестратор этапа 07d, диспатчит sub-агентов и управляет STATE.yaml
- [[icon-generator]] — генерирует ONE иконку через codex image_gen с кэш-лукапом
- [[infographic-builder]] — генерирует ONE инфографику; использует OpenDesign JSON если найден матч
- [[visual-generation]] — скилл, объединяет slot-scanner, prompt-picker, visual-cache и codex-обёртки
- [[landing-visuals]] — команда `/landing-visuals`, точка входа пользователя
- [[block-composition]] — скилл PR-A, расширяется для ветки icon/infographic в inject-content.py
- [[block-composer]] — агент PR-A, создаёт composed.html который является входом для PR-C
- [[07d-visuals]] — этап 07d в pipeline (wiki-страница самого этапа)

## Источник

- `docs/superpowers/plans/2026-05-13-visual-generation-plan.md`