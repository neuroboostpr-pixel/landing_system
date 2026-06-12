---
slug: design-tokens-generation
type: skill
name: "Генерация дизайн-токенов"
stage: "05"
tags: [design-system, tokens, brand-kit, css, typography, color]
triggers: [landing-design]
inputs: [04_БРЕНД/brand-kit.md]
outputs: [05_ДИЗАЙН-СИСТЕМА/DESIGN.md, 05_ДИЗАЙН-СИСТЕМА/tokens.json, 05_ДИЗАЙН-СИСТЕМА/design-preview.html]
gates: []
pre_reqs: [brand-architect]
related: [design-system-generator, brand-architect, block-composer, frontend-builder]
sources: ["skills/design-tokens-generation/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Генерация дизайн-токенов

## Что делает

Скилл читает YAML-frontmatter из `04_БРЕНД/brand-kit.md` и строит полный набор дизайн-токенов для проекта. На выходе — два машиночитаемых артефакта: `DESIGN.md` (9 обязательных секций: Color, Typography, Spacing, Layout, Components, Motion, Voice, Brand, Anti-patterns) и `tokens.json` (CSS-переменные для темы WordPress). Дополнительно рендерится `design-preview.html` для визуальной проверки палитры и типографики. После утверждения этапа одобренные палитры экспортируются в глобальную библиотеку `presets/palettes.yaml`, чтобы повторно использоваться в других проектах.

## Когда вызывается

Запускается агентом `design-system-generator` на этапе 05, после того как бренд-кит утверждён на этапе 04. Вручную вызывается командой `/landing-design` из папки проекта.

## Вход → выход

**Вход:** `04_БРЕНД/brand-kit.md` с заполненным YAML-frontmatter (цвета, шрифты, тон бренда, реквизиты).

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — 9-секционный документ дизайн-системы (Color / Typography / Spacing / Layout / Components / Motion / Voice / Brand / Anti-patterns).
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — JSON с CSS-переменными для темы.
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — HTML-превью для визуальной проверки.
- `presets/palettes.yaml` — обновляется после approve (экспорт новых палитр в глобальную библиотеку).

## Failure modes

- **brand-kit.md отсутствует или не содержит YAML-frontmatter** — скрипт упадёт с KeyError; этап 04 должен быть закрыт до запуска.
- **Экспорт палитры вызван до approve** — черновые палитры попадут в глобальную библиотеку; инвариант нарушен, нужно удалить вручную.
- **Коллизия palette-id в presets/palettes.yaml** — скрипт пропускает существующий id с notice, новая палитра не перезаписывает старую; если нужно обновить — исправлять вручную.
- **Отсутствие одной из 9 секций в DESIGN.md** — downstream-агенты (`block-composer`, `frontend-builder`) получат неполный контракт и могут сгенерировать некорректную вёрстку.
- **design-preview.html не открывается** — не является blocking-gate, но мешает визуальному approve; проверить путь к файлу и права на запись.

## Related

- [[design-system-generator]] — агент, который вызывает этот скилл на этапе 05
- [[brand-architect]] — формирует brand-kit.md, который является входом скилла
- [[block-composer]] — использует tokens.json и DESIGN.md при сборке composed.html
- [[frontend-builder]] — потребляет tokens.json для генерации CSS темы на этапе 08