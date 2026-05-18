На основе предоставленного источника генерирую wiki-страницу:

---
type: block
name: glass-00
sources: ["block-library/_patterns/glass-00/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses:
  - block-composition
  - design-tokens-generation
tags: ["pattern", "css", "glassmorphism", "visual-effect", "backdrop-filter"]
---

# Glass 0 — Glassmorphism-паттерн

## Что делает
Добавляет эффект «стеклянной панели» на элементы лендинга: полупрозрачный фон с размытием подложки (`backdrop-filter: blur`). Создаёт ощущение глубины и premium-стиля без тяжёлых изображений.

## Когда вызывать / в каком этапе
Применяется на этапе **07b (Compose)** — когда `block-composer` собирает `composed.html` и выбирает визуальный стиль карточек, hero-блоков или оверлеев. Патерн подключается через систему CSS-переменных из `tokens.json`, сгенерированных на этапе 05 (design-system).

Подходит для проектов с тёмным или насыщенным фоном (авто, недвижимость, luxury-ниши), где нужен современный UI без плоского дизайна.

## Что на вход / на выход

**Вход:**
- `meta.yaml` — декларация паттерна (id, описание, метод импорта)
- CSS-переменные из `tokens.json` (цвет фона, прозрачность, радиус скругления)

**Выход:**
- CSS-класс/миксин с `backdrop-filter: blur(...)` и `background: rgba(...)`
- Готов к подключению в `composed.html` и финальную тему WordPress

**Ограничение совместимости:** `backdrop-filter` не поддерживается в Firefox без флага (до версии 103). При использовании рекомендуется добавлять fallback-фон.

## Связанные концепты
- [[block-composition]] — оркестрирует применение паттернов при сборке composed.html
- [[design-tokens-generation]] — поставляет CSS-переменные цвета и прозрачности, которые параметризуют стекло
- [[block-library-management]] — управляет реестром паттернов, куда зарегистрирован glass-00
- [[wp-gutenberg-block-builder]] — переносит паттерн в финальную WordPress-тему на этапе 08

## Источник
- `block-library/_patterns/glass-00/meta.yaml`