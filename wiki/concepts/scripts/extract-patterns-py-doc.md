---
type: unknown
name: extract-patterns
sources: ["scripts/extract-effects/extract-patterns.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: []
tags: ["css", "animation", "effects", "patterns", "extract", "script"]
---

# extract-patterns — парсер CSS-эффектов

## Что делает
Анализирует папки со скреипнутыми CSS-файлами и извлекает из них готовые премиум-паттерны: анимации, hover-эффекты, glassmorphism, scroll-триггеры и другие визуальные техники. Результат — структурированный JSON, пригодный для пополнения block-library или design-системы.

## Когда вызывать / в каком этапе
Запускается вручную — как правило, при наполнении или обновлении библиотеки блоков на основе реальных референс-сайтов. Используется разработчиком системы, а не в рамках стандартного 12-этапного workflow лендинга.

## Что на вход / на выход

**Вход:**
- Один или несколько путей к директориям со скреипнутыми CSS-файлами:
  ```
  python extract-patterns.py <scraped-dir> [<scraped-dir> ...]
  ```

**Выход:**
- JSON в stdout вида `{pattern_name: [match_strings...]}`, где каждый ключ — тип найденного паттерна, значение — список найденных CSS-фрагментов.

**Список паттернов, которые ищет скрипт:**

| Паттерн | Что ищет |
|---|---|
| `keyframes` | `@keyframes` — CSS-анимации |
| `transitions` | `transition:` — плавные переходы |
| `hover_states` | `:hover` — стили при наведении |
| `reduced_motion` | `@media (prefers-reduced-motion)` |
| `backdrop_blur` | `backdrop-filter`, `filter` |
| `transforms` | `transform: translate3d`, `scale`, `rotate` |
| `clip_mask` | `clip-path`, `mask-image` |
| `pseudo_decorative` | `::before`, `::after` |
| `grid_auto` | `grid` с `auto-fit` / `auto-fill` |
| `container_queries` | CSS Container Queries |
| `scroll_timeline` | `@scroll-timeline`, scroll-driven анимации |

## Связанные концепты
Явных ссылок на другие концепты системы в исходнике нет. Скрипт является автономной утилитой препроцессинга.

## Источник
- `scripts/extract-effects/extract-patterns.py`