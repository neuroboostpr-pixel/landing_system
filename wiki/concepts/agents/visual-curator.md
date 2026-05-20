---
type: agent
name: visual-curator
sources: ["agents/visual-curator.md"]
updated: 2026-05-20
triggers: ["/landing-visuals", "сгенерируй иконки", "создай инфографику", "запусти визуалы"]
stage: "07d"
uses: ["icon-generator", "infographic-builder", "block-composer", "design-system-generator"]
tags: ["visual", "icons", "infographics", "stage-07d", "pr-c"]
---

# visual-curator — Оркестратор генерации визуалов (этап 07d)

## Что делает

Сканирует готовый `composed.html` на наличие незаполненных слотов для иконок и инфографики, запускает AI-генерацию PNG-файлов под бренд проекта и вставляет результаты обратно в страницу — вместо текстовых плейсхолдеров появляются реальные изображения.

## Когда вызывать / в каком этапе

Вызывается командой `/landing-visuals` на этапе **07d** после того, как утверждена дизайн-система (этап 05) и собран `composed.html` (этап 07b). Агент проверяет оба условия перед запуском — если хотя бы одно не выполнено, выдаёт русское сообщение об ошибке и останавливается.

Поддерживает опциональные флаги:
- `--type icons` / `--type infographics` — частичный прогон только одного типа
- `--force` — игнорировать кэш, перегенерировать всё
- `--slot <name>` — обработать один конкретный слот

## Что на вход / на выход

**Вход:**
- `<project>/.landing-state.yaml` — должен содержать `stages.05_design.status == approved`
- `<project>/07b_COMPOSED/composed.html` — файл с плейсхолдерами вида `[SLOT: feature-1-icon]`
- `tokens.json` и `market-profile.md` — для брендового стиля генерации

**Выход:**
- `<project>/07d_VISUALS/icons/` — PNG-иконки по каждому icon-слоту
- `<project>/07d_VISUALS/infographics/` — PNG-инфографика по каждому infographic-слоту
- `<project>/07d_VISUALS/_slots.yaml` — реестр найденных слотов
- `<project>/07d_VISUALS/STATE.yaml` — статус выполнения (scan / generate / inject)
- обновлённый `composed.html` — плейсхолдеры заменены на `<img class="lp-icon">` и аналоги

## Процесс (4 шага)

1. **Scan** — `slot-scanner.py` обходит `composed.html` и составляет `_slots.yaml`
2. **Иконки** — диспатчит `icon-generator` для каждого icon-слота; кэш по хэшу (hint + стиль + цвет + ниша) исключает повторную генерацию
3. **Инфографика** — то же через `infographic-builder`
4. **Inject** — `compose-blocks.py` читает папки `07d_VISUALS/` и заменяет плейсхолдеры; если папки нет — поведение прежнее (backward compatible)

Правила identity-safe **не применяются**: иконки и инфографика не содержат людей.

## Связанные концепты

- [[icon-generator]] — генерирует один PNG-иконку через codex image_gen
- [[infographic-builder]] — генерирует одну PNG-инфографику через codex image_gen
- [[block-composer]] — создаёт `composed.html` (предшественник, этап 07b)
- [[design-system-generator]] — поставляет `tokens.json` и бренд-палитру для промптов
- [[landing-visuals]] — slash-команда, запускающая этот агент

## Источник

- `agents/visual-curator.md`