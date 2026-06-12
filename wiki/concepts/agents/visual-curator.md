---
slug: visual-curator
type: agent
name: "Куратор визуалов"
stage: "07e"
tags: [visuals, icons, infographics, pr-c, codex, generation]
triggers: [landing-visuals]
inputs:
  - 07b_COMPOSED/composed.html
  - .landing-state.yaml
  - tokens.json
outputs:
  - 07d_VISUALS/_slots.yaml
  - 07d_VISUALS/icons/
  - 07d_VISUALS/infographics/
  - 07d_VISUALS/STATE.yaml
pre_reqs: [design-system-generator, block-composer]
related: [icon-generator, infographic-builder, block-composer, design-system-generator, photo-curator]
sources: ["agents/visual-curator.md"]
updated: 2026-05-26
confidence: {stage: low}
---

# Куратор визуалов

## Что делает

Оркестрирует этап генерации визуальных ассетов (07e). Сканирует `composed.html` в поисках слотов-плейсхолдеров вида `[SLOT: feature-1-icon]`, диспатчит суб-агентов `icon-generator` и `infographic-builder` для каждого слота, управляет кэшем по хэшу (hint + стиль + бренд-цвет + ниша) и, после генерации, инжектирует PNG обратно в `composed.html`. Люди в создаваемых ассетах не фигурируют — identity-safe правила не применяются.

## Когда вызывается

Запускается командой `/landing-visuals` — вручную или через `landing-orchestrator` на этапе 07e. Перед стартом проверяет два hard gate: этап 05 (дизайн-система) в статусе `approved` и наличие `07b_COMPOSED/composed.html`. При провале любого условия немедленно завершается с сообщением на русском.

## Вход → выход

**Вход:** `07b_COMPOSED/composed.html` со слотами-плейсхолдерами; `tokens.json` с бренд-цветами; `market-profile.md` с данными ниши; `.landing-state.yaml` для проверки статусов этапов.

**Выход:** `07d_VISUALS/icons/*.png` и `07d_VISUALS/infographics/*.png`; обновлённый `composed.html` с тегами `<img class="lp-icon">` вместо плейсхолдеров; `07d_VISUALS/_slots.yaml` с каталогом всех найденных слотов; `07d_VISUALS/STATE.yaml` с прогрессом, ошибками и предупреждениями по каждому суб-этапу (scan / generate / inject).

## Failure modes

- Этап 05 не в статусе `approved` или отсутствует `composed.html` — агент останавливается на hard gate до устранения причины.
- `slot-scanner.py` не обнаруживает ни одного слота — генерация не запускается, composed остаётся без изменений.
- Ошибка codex API на конкретном слоте — слот сохраняется как плейсхолдер, ошибка фиксируется в `STATE.yaml::errors`, остальные слоты генерируются в штатном режиме.
- Инжекция через `compose-blocks.py` не находит директорию `07d_VISUALS/` — fallback на исходное поведение с плейсхолдерами без аварийного завершения.
- Повторный запуск без `--force` пропускает уже кэшированные слоты; изменение hint или бренд-цвета порождает новый хэш и требует явного `--force` для перегенерации.

## Related

- [[icon-generator]] — суб-агент, генерирует PNG-иконки для соответствующих слотов
- [[infographic-builder]] — суб-агент, генерирует PNG-инфографику
- [[block-composer]] — создаёт `composed.html`, который служит входом для visual-curator
- [[design-system-generator]] — hard prerequisite: этап 05 должен быть в статусе approved
- [[photo-curator]] — параллельный этап 07d (фото клиента), выполняется одновременно с визуалами