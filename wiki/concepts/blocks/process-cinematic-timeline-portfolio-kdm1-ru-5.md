---
type: block
name: process-cinematic-timeline-portfolio-kdm1-ru-5
sources: ["block-library/process/process-cinematic-timeline-portfolio-kdm1-ru-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "cinematic", "timeline", "ru-market", "services", "tech", "education"]
---

# Процессный блок: центральный персонаж + симметричные шаги

## Что делает

Отображает последовательность шагов процесса в виде таймлайна: по центру — ключевой персонаж или образ, по сторонам симметрично расположены шаги. Фон — сеточный паттерн в кинематографическом стиле.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — `ux-composer` подбирает блок из библиотеки под прототип клиента. Подходит для ниш **услуги**, **tech**, **образование**, когда нужно визуально показать процесс работы с компанией или шаги получения продукта. Стиль `cinematic` сочетается с landing-проектами с тёмной темой или premium-позиционированием.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок блока процесса
- Контекст бренда из `tokens.json` (цвета, шрифты) — инжектируется на этапе 07b

**Выход:**
- HTML-секция блока в составе `wireframe.html` (этап 07a)
- После `/landing-compose` — секция встраивается в `07b_COMPOSED/composed.html` с реальными токенами и текстами из прототипа

## Дополнительные характеристики

| Поле | Значение |
|---|---|
| `layout_pattern` | timeline |
| `style_mood` | cinematic |
| `has_animation` | false |
| `ru_market` | true |
| Источник импорта | portfolio.kdm1.ru (PDF) |
| Метод импорта | codex-block-generation |

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe на этапе 07a
- [[wireframe-rendering]] — рендерит блок в интерактивный `wireframe.html` с 2–3 вариантами
- [[block-composition]] — на этапе 07b инжектирует design-токены и тексты прототипа в блок
- [[block-library-management]] — управляет каталогом блоков, включая регистрацию этого блока

## Источник

- `block-library/process/process-cinematic-timeline-portfolio-kdm1-ru-5/meta.yaml`