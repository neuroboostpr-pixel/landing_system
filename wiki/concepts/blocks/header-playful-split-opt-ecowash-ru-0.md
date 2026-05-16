---
type: block
name: header-playful-split-opt-ecowash-ru-0
sources: ["block-library/header/header-playful-split-opt-ecowash-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags: ["header", "navigation", "playful", "split", "ru-market", "ecommerce", "services", "b2b-saas"]
---

# Компактная навигация на ярком фоне (header-playful-split)

## Что делает

Блок верхней навигации сайта в игривом стиле: логотип слева, пункты меню по центру, кнопка контактного действия справа — всё на ярком цветном фоне. Подходит для интернет-магазинов, сервисных компаний и B2B-продуктов.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** и **07b (Compose)**. Агент [[ux-composer]] выбирает этот блок из библиотеки при подборе шапки для проектов с игривым (`playful`) настроением бренда и `split`-паттерном раскладки. [[block-composer]] инжектирует токены дизайна и тексты прототипа при рендере `composed.html`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — текст для слота `heading` (обязателен, `required: true`)
- `tokens.json` — цвета и типографика из дизайн-системы (бренд-фон, шрифты)
- `selections.yaml` — подтверждённый выбор блока пользователем

**Выход:**
- HTML-фрагмент навигации, встроенный в `wireframe.html` (этап 07a) и `composed.html` (этап 07b)
- Один слот `heading` типа `text` — заголовок/название бренда в шапке

## Особенности блока

| Свойство | Значение |
|---|---|
| Категория | `header` |
| Стиль | `playful` — яркий фон, живые цвета |
| Раскладка | `split` — логотип + меню + CTA по трём зонам |
| Анимации | нет (`has_animation: false`) |
| Рынок | Русскоязычный (`ru_market: true`) |
| Источник | [opt.ecowash.ru](https://opt.ecowash.ru/) — импорт 2026-05-16 через codex-block-generation |

## Подходящие ниши

- `ecommerce` — интернет-магазины
- `services` — сервисные компании
- `b2b-saas` — B2B-продукты и SaaS

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe.html на этапе 07a
- [[block-composer]] — рендерит блок в composed.html с токенами на этапе 07b
- [[wireframe-rendering]] — скилл, управляющий подбором и рендером блоков из библиотеки
- [[block-composition]] — скилл финального сборки composed.html
- [[block-library-management]] — управляет каталогом блоков, куда входит этот блок
- [[design-tokens-generation]] — поставляет цвета и шрифты для инжекции в блок

## Источник

- `block-library/header/header-playful-split-opt-ecowash-ru-0/meta.yaml`