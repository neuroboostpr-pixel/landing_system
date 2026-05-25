---
type: skill
name: design-tokens-generation
sources: ["skills/design-tokens-generation/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "05"
uses: ["design-system-generator", "brand-kit-build", "landing-design"]
tags: ["design-system", "tokens", "brand", "stage-05"]
---

# Design Tokens Generation — Генерация дизайн-системы из бренд-кита

## Что делает

Берёт бренд-кит (`brand-kit.md`) и автоматически строит полную дизайн-систему проекта: файл `DESIGN.md` с 9 секциями (цвета, типографика, отступы, сетка, компоненты, анимации, голос бренда, атмосфера, антипаттерны) и машино-читаемый `tokens.json`. После утверждения этапа — экспортирует палитру в общую библиотеку пресетов.

## Когда вызывать / в каком этапе

Запускается агентом `design-system-generator` на **этапе 05 (Дизайн-система)**, сразу после того как этап 04 (Бренд) завершён и `brand-kit.md` утверждён пользователем. Вызов до утверждения бренд-кита запрещён — черновые палитры не должны попадать в общую библиотеку.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — YAML frontmatter с параметрами бренда (цвета, шрифты, тон)

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — 9-секционный документ дизайн-системы (цвета/роли/контраст, типографика, spacing, layout 12-колонок, компоненты, motion, voice, brand, anti-patterns)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены в машино-читаемом формате для последующих этапов
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — визуальный HTML-превью дизайн-системы
- `presets/palettes.yaml` — пополняется новой палитрой **после** approve (идемпотентно, существующие id не перезаписываются)

**Скрипты:**
- `scripts/build-tokens.py <project-dir>` — основной генератор
- `scripts/render-preview.py <project-dir>` — генератор превью
- `scripts/export-palettes-to-library.py` — постапрув-хук экспорта палитры

## Связанные концепты

- [[design-system-generator]] — агент, который вызывает этот скилл на этапе 05
- [[brand-kit-build]] — предыдущий этап; его выход (`brand-kit.md`) является входом этого скилла
- [[landing-design]] — slash-команда `/landing-design`, запускающая этап 05 целиком
- [[landing-compose]] — этап 07b потребляет `tokens.json` для инжекции CSS-переменных в `composed.html`

## Источник

- `skills/design-tokens-generation/SKILL.md`