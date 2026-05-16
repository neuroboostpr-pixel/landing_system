---
type: block
name: process-editorial-grid-2-romanmelnikov-tilda-4
sources: ["block-library/process/process-editorial-grid-2-romanmelnikov-tilda-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["process", "editorial", "grid-2", "ru-market", "no-animation", "services", "education", "tech"]
---

# Текстовый разбор с крупным заголовком и контурной кнопкой

## Что делает
Блок типа «process» в редакционном стиле: крупный заголовок, несколько абзацев текста и тонкая контурная кнопка. Подходит для подробного описания процесса работы или услуги без визуальной перегрузки.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** — агент [[ux-composer]] подбирает блок из библиотеки при составлении wireframe.html. Также задействуется на этапе **07b (Block Compose)** агентом [[block-composer]], когда пользователь выбрал этот вариант в selections.yaml.

Подходит для проектов в нишах:
- **services** — описание услуг и процесса оказания
- **education** — разбор программы обучения или методики
- **tech** — технические объяснения продукта

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — крупный заголовок блока
- Текстовые абзацы из `prototype.yaml` (подставляются при compose)
- Токены дизайна из `tokens.json` (цвет, шрифт, отступы)

**Выход:**
- HTML-фрагмент блока в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Контурная кнопка рендерится через CSS outline-стиль без заливки

**Особенности:**
- `has_animation: false` — блок статичен, без JS-анимаций
- `ru_market: true` — адаптирован под российский рынок
- `layout_pattern: grid-2` — двухколоночная сетка

## Связанные концепты
- [[ux-composer]] — выбирает блок при построении wireframe на этапе 07a
- [[block-composer]] — рендерит блок в composed.html на этапе 07b
- [[block-composition]] — скилл, управляющий инъекцией токенов и текстов в блок
- [[wireframe-rendering]] — скилл, генерирующий wireframe.html из block-library

## Источник
- `block-library/process/process-editorial-grid-2-romanmelnikov-tilda-4/meta.yaml`