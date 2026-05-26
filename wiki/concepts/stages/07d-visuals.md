---
slug: 07d-visuals
type: stage
name: "07d — Иконки и инфографика"
stage: "07d"
tags: [visuals, icons, infographics, ai-generation, codex, image-gen]
triggers: [landing-visuals]
inputs:
  - landing-compose
  - 05-dizayn-sistema
outputs:
  - 07d-visuals
gates: [visuals_slots_filled]
pre_reqs:
  - 05-dizayn-sistema
  - landing-compose
related:
  - landing-visuals
  - visual-generation
  - icon-generator
  - infographic-builder
  - landing-compose
  - gpt5-prompting-engine
sources: ["template/07d_VISUALS/README.md"]
updated: 2026-05-26
confidence:
  gates: low
---

# 07d — Иконки и инфографика

## Что делает

На этом этапе система автоматически генерирует PNG-иконки и инфографику для лендинга через codex (gpt-image-2). Скилл сканирует `07b_COMPOSED/composed.html`, находит слоты с `data-slot-type="icon"` и `data-slot-type="infographic"`, и для каждого создаёт изображение под брендинг проекта — с учётом цветов из `tokens.json` и ниши из `market-profile.md`. После генерации `composed.html` перерендерится: placeholder `[SLOT: ...]` заменяется на тег `<img>`. Результаты кэшируются по хэшу (hint + style + brand_color + niche) — повторный запуск не тратит API-кредиты на уже сгенерированные слоты.

## Когда вызывается

Вызывается вручную командой `/landing-visuals` после того, как утверждены этап 05 (design-system) и этап 07b (composed.html существует и содержит визуальные слоты). В оркестраторе — параллельно с этапом 07c (photos).

## Вход → выход

**Вход:** `07b_COMPOSED/composed.html` со слотами `data-slot-type="icon"/"infographic"`, `tokens.json` с цветами бренда, `market-profile.md` с нишей проекта.

**Выход:** `icons/<slot>.png` и `infographics/<slot>.png` — сгенерированные PNG; `_slots.yaml` — список найденных слотов; `prompts.yaml` — аудит-лог (какой промпт дал какой PNG); `STATE.yaml` — статус этапа; `.cache/<hash>.png` — локальный кэш.

## Чем закрывается этап (gates)

- visuals_slots_filled — все слоты в composed.html закрыты реальными `<img>`, ни одного оставшегося placeholder `[SLOT: ...]` типа icon/infographic.

## Failure modes

- Слоты не найдены в composed.html — этап 07b не завершён или атрибуты `data-slot-type` отсутствуют в разметке.
- codex API недоступен или кончился лимит — генерация падает, кэш пуст; нужен `--force` после пополнения.
- Некорректный `tokens.json` — codex получает неверный brand_color, иконки выходят не в брендинге.
- Ручная правка PNG в `icons/` или `infographics/` — будет перезаписана при следующем `--force`.
- `.cache/` случайно попал в git — замедляет репозиторий; должен быть в `.gitignore`.

## Related

- [[landing-visuals]] — slash-команда, запускающая этот этап
- [[visual-generation]] — скилл-реализация pipeline генерации
- [[icon-generator]] — субагент генерации иконок
- [[infographic-builder]] — субагент генерации инфографики
- [[landing-compose]] — предшествующий этап, создающий composed.html со слотами
- [[gpt5-prompting-engine]] — движок промптов для codex image_gen