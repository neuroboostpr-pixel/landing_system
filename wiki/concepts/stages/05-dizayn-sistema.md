---
type: stage
name: design-system
sources: ["template/05_ДИЗАЙН-СИСТЕМА/README.md"]
updated: 2026-05-15
triggers: []
stage: "05"
uses: ["design-system-generator", "brand-architect", "brand-kit-build", "design-tokens-generation"]
tags: ["design", "tokens", "stage-05"]
---

# 05 — Дизайн-система

## Что делает
Превращает бренд-кит в машиночитаемые дизайн-токены и единый источник истины о стиле лендинга: цвета, шрифты, отступы, визуальный preview.

## Когда вызывать / в каком этапе
Запускается на этапе 05 после того, как [[brand-architect]] завершил этап 04 и создал `04_БРЕНД/brand-kit.md`. Агент [[design-system-generator]] читает brand-kit и генерирует артефакты этапа.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — готовый бренд-кит от [[brand-architect]]

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины: цвета, шрифты, отступы, компоненты
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены для инжекции в блоки
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — визуальный preview дизайн-системы для согласования с клиентом

## Связанные концепты
- [[design-system-generator]] — агент, который создаёт все артефакты этапа 05
- [[brand-architect]] — предшествующий агент: производит brand-kit.md, который является входом для этого этапа
- [[brand-kit-build]] — скилл, которым владеет brand-architect
- [[design-tokens-generation]] — скилл, которым владеет design-system-generator; описывает логику генерации tokens.json и DESIGN.md
- [[stack-planner]] — следующий этап (06): читает DESIGN.md при выборе плагинов и библиотек
- [[block-composition]] — этап 07b: потребляет tokens.json при инжекции токенов в composed.html

## Источник
- `template/05_ДИЗАЙН-СИСТЕМА/README.md`