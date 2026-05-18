---
type: rule
name: palettes
sources: ["presets/palettes.yaml"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-design", "design-tokens-generation", "design-system-generator"]
tags: ["palette", "tokens", "color", "design-system", "presets"]
---

# Palettes — библиотека глобальных палитр

## Что делает
Хранит готовые цветовые палитры в виде дизайн-токенов. Когда маркетолог запускает `/landing-design`, система предлагает выбрать палитру из этой библиотеки — и все цвета лендинга автоматически применяются без ручной настройки.

## Когда вызывать / в каком этапе
Файл используется на этапе **05 — дизайн-система** (`/landing-design`). После того как `design-system-generator` или `brand-architect` утверждают набор токенов, палитра может быть сохранена сюда для повторного использования в других проектах. Пополнение — вручную или через `/landing-design` после финального approve.

## Что на вход / на выход
**Вход:** YAML-файл с массивом `palettes`, каждая запись содержит `id`, `name`, `description`, `created_at`, `created_in_project` и блок `tokens` с ~18 CSS-переменными.

**Выход:** Набор токенов (`tokens.json` / DESIGN.md) для конкретного проекта — агент копирует нужные значения и подставляет в дизайн-систему.

### Текущие палитры (4 шт.)

| id | name | Фон | Акцент |
|---|---|---|---|
| `nu-paper` | Бумажный | `#F8F7F4` светлый | Изумрудный `#047857` |
| `nu-quiet-dark` | Тихий-тёмный | `#0A0A0B` чёрный | Мятный `#10B981` |
| `nu-beige` | Бежевый | `#FBF7F0` тёплый | Красный `#DC2626` |
| `nu-iqido` | IQIDO Guideline | `#0E2B30` тёмно-морской | Бирюза + коралл `#77D9D9` / `#E85E48` |

Все четыре мигрированы из проекта `neuroupgrade-v2` (2026-05-12).

### Структура токена
Каждая палитра задаёт: `bg_base`, `bg_section`, `bg_elevated`, `border_subtle`, `border_strong`, `text_primary`, `text_soft`, `text_dim`, `accent_*` (mint, teal, coral, coral_hover, coral_text, rgb-значения), `card_bg`, `card_border`, `card_border_hover`, `accent_cta_glow_opacity`.

## Связанные концепты
- [[landing-design]] — команда, которая предлагает выбрать палитру и записывает её в проект
- [[design-tokens-generation]] — скилл, который превращает палитру в `tokens.json` и CSS-переменные
- [[design-system-generator]] — агент, читающий токены при генерации DESIGN.md
- [[brand-kit-build]] — агент, который может добавить новую палитру в этот файл после финального approve

## Источник
- `presets/palettes.yaml`