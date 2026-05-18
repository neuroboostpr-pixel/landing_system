---
type: block
name: header-corporate-split-zilant-group-0
sources: ["block-library/header/header-corporate-split-zilant-group-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["header", "corporate", "split", "navigation", "ru-market"]
---

# Header Corporate Split — Zilant Group

## Что делает

Компактная верхняя навигация с логотипом по центру зоны меню и мягкой кнопкой действия справа. Подходит для строгих корпоративных и B2B-сайтов: нет анимаций, акцент на структуру и читаемость.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** и **07b (Block Compose)**, когда [[ux-composer]] выбирает блок хедера из библиотеки. Подходит для ниш:
- `services` — услуги
- `b2b-saas` — B2B-платформы
- `education` — образование

Ориентирован на **российский рынок** (`ru_market: true`). Выбирается при макете типа `split` и визуальном настроении `corporate`.

## Что на вход / на выход

**Слоты (обязательные):**
| Имя слота | Тип | Обязательный |
|-----------|-----|-------------|
| `heading` | text | ✅ да |

**На вход:** `prototype.yaml` с содержимым блока (заголовок/название бренда), `tokens.json` с цветами и шрифтами.

**На выход:** HTML-фрагмент хедера, вставленный в `wireframe.html` (этап 07a) и в `composed.html` (этап 07b) с подставленными токенами и текстом прототипа.

## Особенности

- `has_animation: false` — никаких переходов и GSAP-эффектов, статичный хедер
- `layout_pattern: split` — логотип и кнопка разнесены в разные стороны
- Импортирован с сайта [zilant.group](https://zilant.group/) методом `codex-block-generation`

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при составлении wireframe
- [[block-composer]] — рендерит блок в composed.html с токенами
- [[wireframe-rendering]] — скилл, который использует мета-данные блока при построении wireframe.html
- [[block-composition]] — скилл этапа 07b, инжектирует design-токены в шаблон блока
- [[block-library-management]] — управляет каталогом, в котором зарегистрирован этот блок

## Источник

- `block-library/header/header-corporate-split-zilant-group-0/meta.yaml`