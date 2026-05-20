---
type: agent
name: visual-curator
sources: ["agents/visual-curator.md"]
updated: 2026-05-20
triggers: ["/landing-visuals", "сгенерируй иконки", "создай инфографику", "stage 07d visuals"]
stage: "07d"
uses: ["icon-generator", "infographic-builder", "block-composer", "landing-visuals"]
tags: ["visual", "icons", "infographics", "stage-07d", "pr-c"]
---

# visual-curator — Оркестратор генерации визуалов (этап 07d)

## Что делает

Сканирует `composed.html` на наличие слотов под иконки и инфографику, запускает AI-генерацию PNG через суб-агентов, кэширует результаты и вставляет готовые изображения обратно в `composed.html`. Работает без идентити-safe ограничений — люди в иконках и чартах не появляются.

## Когда вызывать / в каком этапе

Активируется командой `/landing-visuals` на этапе **07d** (PR-C). Два жёстких предусловия:
- `stages.05_design.status == approved` в `.landing-state.yaml` — дизайн-система утверждена.
- Файл `07b_COMPOSED/composed.html` существует — прошёл PR-A (compose).

Если хотя бы одно условие не выполнено — агент останавливается с русским сообщением. Принимает опциональные флаги: `--type icons`, `--type infographics`, `--force` (игнорировать кэш), `--slot <name>` (один слот).

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — собранная страница с `[SLOT: ...]` placeholders
- `04_БРЕНД/tokens.json` — бренд-цвета и стиль (используют суб-агенты при генерации)
- `.landing-state.yaml` — текущий статус pipeline

**Выход:**
- `07d_VISUALS/_slots.yaml` — обнаруженные слоты (scan-артефакт)
- `07d_VISUALS/icons/*.png` — иконки под каждый icon-слот
- `07d_VISUALS/infographics/*.png` — инфографика под каждый infographic-слот
- `07d_VISUALS/STATE.yaml` — трекинг состояния (`scan → generate → inject`)
- Обновлённый `composed.html` — placeholders заменены на `<img class="lp-icon">` / `<img class="lp-infographic">`

## Процесс

1. **Scan** — `slot-scanner.py` находит все слоты в HTML.
2. **Generate icons** — для каждого icon-слота диспатчит [[icon-generator]]; хэш-кэш пропускает codex если PNG уже есть.
3. **Generate infographics** — для каждого infographic-слота диспатчит [[infographic-builder]]; логика кэша та же.
4. **Inject** — `compose-blocks.py` читает `07d_VISUALS/` и вшивает PNG в `composed.html`. Обратная совместимость: если папка отсутствует — placeholders сохраняются.
5. Отмечает `stages.inject` в STATE.yaml и печатает русский итог.

## Связанные концепты

- [[icon-generator]] — суб-агент для генерации одной иконки через codex image_gen
- [[infographic-builder]] — суб-агент для генерации одного инфографика
- [[block-composer]] — предшественник: создаёт `composed.html` на этапе 07b
- [[landing-visuals]] — команда-триггер для запуска этого агента
- [[visual-generation]] — скилл с полными правилами генерации визуалов

## Источник

- `agents/visual-curator.md`