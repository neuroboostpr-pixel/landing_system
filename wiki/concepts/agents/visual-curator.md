---
type: agent
name: visual-curator
sources: ["agents/visual-curator.md"]
updated: 2026-05-26
triggers: []
stage: "07d"
uses: ["icon-generator", "infographic-builder", "landing-visuals", "landing-compose", "landing-design"]
tags: ["visuals", "icons", "infographics", "stage-07d", "pr-c"]
---

# visual-curator — Оркестратор генерации визуалов (этап 07d)

## Что делает

Сканирует `composed.html` в поисках слотов для иконок и инфографики, запускает AI-генерацию через дочерних агентов и вставляет готовые PNG обратно в макет. Управляет кэшем и состоянием этапа через `STATE.yaml`.

## Когда вызывать / в каком этапе

Активируется командой `/landing-visuals` на этапе **07d** pipeline. Перед запуском обязательны два условия:
- Этап `05_design` должен быть в статусе `approved` (дизайн-система утверждена).
- Файл `<project>/07b_COMPOSED/composed.html` должен существовать (этап PR-A завершён).

Если хотя бы одно условие не выполнено — агент останавливается с русскоязычным сообщением об ошибке.

## Что на вход / на выход

**На вход:**
- `07b_COMPOSED/composed.html` — скомпонованный HTML с placeholder-слотами вида `[SLOT: feature-1-icon]`.
- `tokens.json` — бренд-токены (цвета, стиль).
- `market-profile.md` — ниша проекта (для стилистики генерации).

**На выход:**
- `07d_VISUALS/icons/*.png` — сгенерированные иконки.
- `07d_VISUALS/infographics/*.png` — сгенерированная инфографика.
- `07d_VISUALS/_slots.yaml` — манифест найденных слотов.
- `07d_VISUALS/STATE.yaml` — статус каждого подэтапа (scan / generate / inject).
- Обновлённый `07b_COMPOSED/composed.html` — placeholders заменены на `<img class="lp-icon">`.

## Процесс

1. **Scan** — `slot-scanner.py` парсит HTML и составляет `_slots.yaml`.
2. **Generate icons** — для каждого icon-слота диспатчит агента `icon-generator`; кэш проверяется через `visual-cache.py` (hash по hint + стиль + бренд-цвет + ниша).
3. **Generate infographics** — аналогично через `infographic-builder`.
4. **Inject** — `compose-blocks.py` считывает папки `07d_VISUALS/` и перерендеривает composed.html.
5. Отмечает `stages.inject: done` в STATE.yaml и выводит сводку на русском.

**Идемпотентность:** повторный запуск пропускает уже кэшированные слоты. Флаг `--force` сбрасывает кэш. Флаг `--slot <name>` перегенерирует один конкретный слот.

## Связанные концепты

- [[icon-generator]] — дочерний агент генерации иконок
- [[infographic-builder]] — дочерний агент генерации инфографики
- [[landing-visuals]] — slash-команда, которая запускает visual-curator
- [[landing-compose]] — этап 07b, создаёт composed.html (обязательный input)
- [[landing-design]] — этап 05, утверждение дизайн-системы (gate)

## Источник

- `agents/visual-curator.md`