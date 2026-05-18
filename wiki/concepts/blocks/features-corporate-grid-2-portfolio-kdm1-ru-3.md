---
type: block
name: features-corporate-grid-2-portfolio-kdm1-ru-3
sources: ["block-library/features/features-corporate-grid-2-portfolio-kdm1-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "grid", "corporate", "ecommerce", "services", "ru-market"]
---

# Сетка товарных категорий — корпоративная (grid-2, KDM1)

## Что делает
Отображает товарные категории или портфолио в виде сетки с карточками разного размера, короткими подписями и тёмными кнопками призыва к действию (CTA). Подходит для корпоративного стиля без анимации.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** и **07b (Compose)** при формировании блока `features` лендинга. Агент [[ux-composer]] выбирает блок из библиотеки при наличии в прототипе секции с товарными категориями или услугами. [[block-composer]] подставляет контент и токены на этапе compose.

Подходит для ниш:
- **ecommerce** — витрина категорий товаров
- **services** — сетка направлений или услуг компании

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции
- Токены дизайна из `tokens.json` (цвета, шрифты) — подставляются [[block-composer]]
- Контент из `prototype.yaml` — тексты карточек и CTA

**Выход:**
- HTML-фрагмент блока `features` с сеткой карточек разного размера, тёмными CTA и короткими подписями, вставленный в `wireframe.html` (этап 07a) и `composed.html` (этап 07b)

**Параметры блока:**
| Параметр | Значение |
|---|---|
| Категория | `features` |
| Паттерн layout | `grid-2` |
| Стиль | `corporate` |
| Анимация | нет |
| Рынок | RU |
| Источник | portfolio.kdm1.ru (PDF), импорт через codex-block-generation |

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при сборке wireframe
- [[block-composer]] — инжектирует design-tokens и тексты прототипа в блок
- [[wireframe-rendering]] — скилл рендеринга, в котором блок участвует как кандидат
- [[block-composition]] — скилл compose-этапа, финализирующий блок в composed.html
- [[block-library-management]] — скилл управления библиотекой, куда входит этот блок

## Источник
- `block-library/features/features-corporate-grid-2-portfolio-kdm1-ru-3/meta.yaml`