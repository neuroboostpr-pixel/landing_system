---
type: block
name: glass-01
sources: ["block-library/_patterns/glass-01/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "frontend-builder"]
tags: ["pattern", "glassmorphism", "css", "visual-effect", "backdrop-filter"]
---

# Glass 1 — Glassmorphism-паттерн

## Что делает
Добавляет к блоку эффект «матового стекла» (glassmorphism): полупрозрачный фон с размытием подложки через CSS-свойство `backdrop-filter`. Используется как декоративный визуальный слой поверх фоновых изображений или градиентов.

## Когда вызывать / в каком этапе
Применяется на этапе **07b (Compose)** — когда block-composer собирает composed.html и нужно наложить стеклянный эффект на карточки, hero-блок или модальные компоненты. Подключается как CSS-паттерн поверх базового блока; не является самостоятельным структурным блоком.

## Что на вход / на выход

**Вход:**
- `meta.yaml` — метаданные паттерна (id, name, description, import_method)
- CSS-класс паттерна применяется к целевому HTML-элементу

**Выход:**
- CSS-правила с `backdrop-filter: blur(...)` и полупрозрачным `background`
- Визуальный эффект матового стекла на целевом элементе в `composed.html` / итоговом теме WordPress

## Детали реализации
- **import_method:** `css-pattern-extraction` — паттерн получен методом извлечения CSS, не написан с нуля
- **imported_at:** 2026-05-16
- Требует поддержки браузером свойства `backdrop-filter` (все современные браузеры; Safari требует префикс `-webkit-backdrop-filter`)
- Совместим с токенами дизайна из `tokens.json` (цвета, прозрачность)

## Связанные концепты
- [[block-composer]] — использует паттерн при рендере composed.html на этапе 07b
- [[frontend-builder]] — применяет паттерн в финальном CSS темы WordPress на этапе 08

## Источник
- `block-library/_patterns/glass-01/meta.yaml`