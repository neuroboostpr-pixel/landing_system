---
type: block
name: features-editorial-split-project21993216-tild-7
sources: ["block-library/features/features-editorial-split-project21993216-tild-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "editorial", "split", "ecommerce", "tech", "services", "ru_market"]
---

# Features Editorial Split — раздел с заголовком, списком и предметным фото

## Что делает
Отображает ключевые преимущества продукта или услуги в редакционном двухколоночном макете: сильный заголовок и текстовый список слева, крупное предметное фото справа. Привлекает внимание к продукту и поддерживает доверие через конкретные факты.

## Когда вызывать / в каком этапе
Используется на этапе **07a (wireframe)** при выборе блока для раздела «Преимущества» или «Особенности». `ux-composer` подбирает блок автоматически из библиотеки по категории `features` и mood `editorial`. После выбора вариантов — задействуется на этапе **07b (compose)** через `block-composer`.

Подходит для ниш:
- **ecommerce** — демонстрация характеристик товара
- **tech** — описание функций продукта
- **services** — перечисление условий и преимуществ услуги

## Что на вход / на выход

**Вход:**
- Слот `heading` (обязательный, тип `text`) — сильный заголовок раздела
- Список текстовых пунктов (левая колонка)
- Фотография предмета/продукта (правая колонка, крупная)

**Выход:**
- HTML-блок в `wireframe.html` с CSS-вариантом в стиле `editorial`
- После compose: блок в `composed.html` с подставленными токенами дизайна и текстом из прототипа

## Технические характеристики
| Параметр | Значение |
|---|---|
| Категория | `features` |
| Стиль | `editorial` |
| Раскладка | `split` (2 колонки) |
| Анимация | нет |
| RU-рынок | да |
| Источник | Tilda (project21993216) |
| Метод импорта | codex-block-generation |

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки на этапе 07a wireframe
- [[block-composer]] — рендерит блок в composed.html на этапе 07b
- [[wireframe-rendering]] — скилл, управляющий рендером wireframe.html
- [[block-composition]] — скилл, управляющий compose-этапом
- [[block-library-management]] — скилл управления библиотекой блоков, куда входит этот блок

## Источник
- `block-library/features/features-editorial-split-project21993216-tild-7/meta.yaml`