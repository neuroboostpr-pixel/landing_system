---
type: skill
name: design-tokens-generation
sources: ["skills/design-tokens-generation/SKILL.md"]
updated: 2026-05-15
triggers: []
stage: "05"
uses: ["brand-kit-build", "design-system-generator", "brand-architect"]
tags: ["design", "tokens", "stage-05", "DESIGN.md"]
---

# Design Tokens Generation — Генерация дизайн-системы

## Что делает

Читает готовый бренд-кит проекта и автоматически собирает полную дизайн-систему: файл `DESIGN.md` с описанием всех визуальных правил и машиночитаемый `tokens.json` с цветами, шрифтами и отступами. Дополнительно рендерит HTML-превью дизайн-системы для визуальной проверки.

## Когда вызывать / в каком этапе

Этап **05 (Дизайн-система)**. Запускается агентом `design-system-generator` после того, как `brand-architect` завершил этап 04 и файл `04_БРЕНД/brand-kit.md` утверждён. Скилл не вызывается вручную — его запускает агент.

После утверждения этапа 05 автоматически срабатывает post-approve хук: скрипт `export-palettes-to-library.py` добавляет новую палитру в глобальную библиотеку `presets/palettes.yaml`. **Важно:** запускать этот хук до утверждения нельзя — черновые палитры не должны попадать в библиотеку.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — YAML-frontmatter с цветами, шрифтами, иконками из бренд-кита

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — 9 секций: Color, Typography, Spacing, Layout, Components, Motion, Voice, Brand, Anti-patterns
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены для сборки темы
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — визуальный превью дизайн-системы в браузере

**Скрипты:**
- `scripts/build-tokens.py <project-dir>` — генерирует DESIGN.md + tokens.json
- `scripts/render-preview.py <project-dir>` — генерирует design-preview.html
- `scripts/export-palettes-to-library.py` — post-approve хук экспорта палитры

**Структура DESIGN.md** включает 9 обязательных секций: палитра с контрастными парами, типографика (display/body/mono, h1–h6), модульная сетка отступов, 12-колоночный лэйаут с breakpoints, стили компонентов (кнопки, инпуты, карточки), motion-токены (duration + easing), тон голоса бренда, атмосфера бренда, явный список анти-паттернов.

## Связанные концепты

- [[brand-kit-build]] — предыдущий этап, создаёт `brand-kit.md`, который является входом для этого скилла
- [[design-system-generator]] — агент-исполнитель, который вызывает этот скилл на этапе 05
- [[brand-architect]] — агент этапа 04, чей артефакт (`brand-kit.md`) служит источником данных

## Источник

- `skills/design-tokens-generation/SKILL.md`