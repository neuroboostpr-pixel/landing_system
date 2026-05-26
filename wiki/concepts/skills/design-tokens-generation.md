---
type: skill
name: design-tokens-generation
sources: ["skills/design-tokens-generation/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: "05"
uses: ["design-system-generator", "brand-kit-build", "landing-design"]
tags: ["design", "tokens", "brand", "stage-05"]
---

# Design Tokens Generation — генерация дизайн-системы из бренд-кита

## Что делает
Читает бренд-кит проекта и автоматически строит полную дизайн-систему: файл `DESIGN.md` с 9 разделами (цвета, типографика, сетка, анимации и т.д.) и машино-читаемый `tokens.json` для использования в теме WordPress.

## Когда вызывать / в каком этапе
Вызывается агентом `design-system-generator` на этапе **05 — Дизайн-система**, после того как бренд-кит (`04_БРЕНД/brand-kit.md`) утверждён пользователем. Не вызывать раньше одобрения этапа 04.

После прохождения gate-check этапа 05 запускается дополнительный post-approve хук: экспорт палитры в глобальную библиотеку `presets/palettes.yaml`. Важно: экспорт нельзя запускать до утверждения — черновики не должны попадать в общую библиотеку.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — YAML frontmatter с цветами, шрифтами и параметрами бренда.

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — полная дизайн-документация, 9 обязательных секций:
  1. Color — палитра, роли цветов, контрастные пары
  2. Typography — шрифтовой стек, масштаб заголовков h1–h6
  3. Spacing — модульная сетка (xs/sm/md/lg/xl)
  4. Layout — 12-колонная сетка, breakpoints, max-widths
  5. Components — стиль кнопок, инпутов, карточек, navbar
  6. Motion — duration-токены, easing, анимируемые элементы
  7. Voice — тон коммуникации, лексика (RU)
  8. Brand — 3–5 ключевых визуальных атмосфер
  9. Anti-patterns — явный список запрещённых решений
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машино-читаемые токены для темы
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — HTML-превью дизайн-системы (через `render-preview.py`)

## Связанные концепты
- [[design-system-generator]] — агент, который вызывает этот скилл на этапе 05
- [[brand-kit-build]] — предшествующий скилл: формирует `brand-kit.md`, который является входом
- [[landing-design]] — slash-команда, запускающая этап 05 целиком

## Источник
- `skills/design-tokens-generation/SKILL.md`