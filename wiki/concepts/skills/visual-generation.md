---
slug: visual-generation
type: skill
name: "Генерация визуалов (иконки и инфографика)"
stage: "07d"
tags: [visuals, icons, infographics, codex, image-gen, pr-c]
triggers: [landing-visuals]
inputs: [07b_COMPOSED/composed.html, 05_ДИЗАЙН/tokens.json, market-profile.md]
outputs: [07d_VISUALS/_slots.yaml, 07d_VISUALS/*.png, 07d_VISUALS/STATE.yaml]
gates: []
pre_reqs: [design-system-generator, block-composer]
related: [visual-curator, icon-generator, infographic-builder, photo-curator, block-composition]
sources: ["skills/visual-generation/SKILL.md"]
updated: 2026-05-26
confidence: {gates: low}
---

# Генерация визуалов (иконки и инфографика)

## Что делает

Скилл генерирует иконки и инфографику для всех visual-слотов в `composed.html` через codex image_gen. Параметризован из `tokens.json` (бренд-цвета) и `market-profile.md` (ниша). Результаты кэшируются по хэшу входных параметров — повторный прогон не делает лишних API-вызовов. После генерации подставляет PNG прямо в `composed.html`, заменяя placeholders вида `[SLOT: feature-1-icon]` на теги `<img class="lp-icon">`.

## Когда вызывается

Вызывается вручную командой `/landing-visuals` после того, как утверждён этап 05 (design-system) и существует `07b_COMPOSED/composed.html`. Поддерживает частичный прогон через флаги `--type icons`, `--type infographics`, `--slot <name>` и принудительную перегенерацию через `--force`.

## Вход → выход

**Вход:** `07b_COMPOSED/composed.html` с placeholder-слотами, `05_ДИЗАЙН/tokens.json` с бренд-цветами, `market-profile.md` с данными ниши.

**Выход:** `07d_VISUALS/_slots.yaml` (список всех слотов), `07d_VISUALS/*.png` (сгенерированные изображения), `07d_VISUALS/STATE.yaml` (прогресс), обновлённый `composed.html` с подставленными `<img>`.

## Failure modes

- **Codex API недоступен или квота исчерпана** — генерация падает, STATE.yaml фиксирует прерванные слоты; перезапуск продолжает с оставшихся.
- **Кэш-коллизия по хэшу** — одинаковый хэш для разных слотов при нестандартных нишах; требует `--force` для перегенерации.
- **slot-scanner не распознаёт кастомный формат placeholder** — слот пропускается молча, `_slots.yaml` неполный; нужна ручная проверка.
- **inject-content.py теряет разметку** — при инъекции PNG в сложные вложенные блоки возможно смещение вёрстки; нужен визуальный контроль `composed.html` после прогона.
- **tokens.json отсутствует или невалиден** — генерация запускается без бренд-цветов, иконки получают дефолтный стиль без брендинга.

## Related

- [[visual-curator]] — агент-владелец скилла, оркестрирует scan → generate → inject
- [[icon-generator]] — субкомпонент для генерации иконок через codex
- [[infographic-builder]] — субкомпонент для генерации инфографики
- [[photo-curator]] — параллельный этап 07c; вместе закрывают визуальный контент composed.html
- [[block-composer]] — создаёт composed.html, который этот скилл дополняет