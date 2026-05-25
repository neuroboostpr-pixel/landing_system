---
type: agent
name: visual-curator
sources: ["agents/visual-curator.md"]
updated: 2026-05-25
triggers: []
stage: "07e_visuals"
uses: ["icon-generator", "infographic-builder", "landing-visuals", "landing-compose", "landing-design"]
tags: ["visuals", "icons", "infographics", "stage-07d", "pr-c"]
---

# visual-curator — Оркестратор генерации визуалов (Stage 07d)

## Что делает

Управляет автоматической генерацией иконок и инфографики для лендинга: сканирует `composed.html`, находит все слоты для визуалов, запускает генерацию через AI (codex), кэширует результаты и вставляет готовые PNG обратно в HTML. Люди в визуалах отсутствуют, поэтому identity-safe ограничения не применяются.

## Когда вызывать / в каком этапе

Запускается командой `/landing-visuals` на этапе **07e_visuals** (PR-C).

Жёсткие предусловия:
- `stages.05_design.status == approved` в `.landing-state.yaml` — дизайн-система должна быть утверждена.
- Файл `07b_COMPOSED/composed.html` должен существовать — сначала нужно пройти PR-A (`/landing-compose`).

Если хотя бы одно условие не выполнено — агент останавливается с русским сообщением об ошибке.

## Что на вход / на выход

**Вход:**
- `<project>/07b_COMPOSED/composed.html` — собранный HTML с плейсхолдерами `[SLOT: feature-1-icon]` и аналогичными.
- `<project>/.landing-state.yaml` — состояние pipeline.
- Кэш `.cache/<hash>.png` — повторный прогон пропускает codex для уже сгенерированных слотов.

**Выход:**
- `<project>/07d_VISUALS/_slots.yaml` — список найденных слотов.
- `<project>/07d_VISUALS/icons/` — PNG иконок.
- `<project>/07d_VISUALS/infographics/` — PNG инфографики.
- `<project>/07d_VISUALS/STATE.yaml` — статус этапов: `scan / generate / inject`.
- Обновлённый `composed.html` — плейсхолдеры заменены на `<img class="lp-icon">`.

## Процесс выполнения

1. **Scan** — `slot-scanner.py` извлекает все слоты из `composed.html` в `_slots.yaml`.
2. **Generate icons** — для каждого иконочного слота диспатчит агент [[icon-generator]] с `(slot_name, hint)`. Сначала проверяет кэш через `visual-cache.py`.
3. **Generate infographics** — аналогично для инфографики через агент [[infographic-builder]].
4. **Inject** — `compose-blocks.py` подтягивает содержимое `07d_VISUALS/` и обновляет `composed.html`. Совместим назад: если `07d_VISUALS/` нет — сохраняет поведение с плейсхолдерами.
5. Обновляет `STATE.yaml`, выводит итог на русском языке.

**Идемпотентность:** флаг `--force` сбрасывает кэш. Флаг `--slot <name>` обрабатывает один конкретный слот.

## Связанные концепты

- [[icon-generator]] — суб-агент генерации иконок через codex image_gen
- [[infographic-builder]] — суб-агент генерации инфографики
- [[landing-visuals]] — slash-команда, триггерирующая этого агента
- [[landing-compose]] — предшествующий этап 07b, создающий `composed.html`
- [[landing-design]] — этап 05, утверждение дизайн-системы (жёсткое предусловие)

## Источник

- `agents/visual-curator.md`