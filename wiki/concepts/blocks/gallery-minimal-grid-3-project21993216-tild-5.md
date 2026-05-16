---
type: block
name: gallery-minimal-grid-3-project21993216-tild-5
sources: ["block-library/gallery/gallery-minimal-grid-3-project21993216-tild-5/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["gallery", "grid-3", "minimal", "ru_market", "ecommerce", "services", "education"]
---

# gallery-minimal-grid-3 — Каталог из трёх карточек категорий

## Что делает

Отображает три крупные карточки категорий с мягкими градиентными фонами. Подходит для витрины услуг, товарных разделов или образовательных направлений — без анимации, в минималистичном стиле.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** агентом `ux-composer` при подборе блоков из библиотеки под прототип. Выбирается, когда нужно структурированно показать 3 категории / направления / раздела в сетке. Особенно актуален для ниш: e-commerce, услуги, образование.

## Что на вход / на выход

**Обязательные слоты:**
| Слот | Тип | Обязательный |
|------|-----|:---:|
| `heading` | text | ✅ |

**Параметры блока:**
- `style_mood`: `minimal` — без декора, чистые градиентные фоны
- `layout_pattern`: `grid-3` — три колонки равной ширины
- `has_animation`: `false` — статичный, без JS-эффектов
- `ru_market`: `true` — адаптирован под русскоязычный рынок

**Выход:** HTML-секция с тремя карточками, готовая к вставке в `wireframe.html` и `composed.html`.

## Связанные концепты

- [[ux-composer]] — отбирает блок из библиотеки при построении wireframe по прототипу
- [[block-library-management]] — управляет каталогом всех блоков, включает этот блок в поиск
- [[wireframe-rendering]] — рендерит блок с вариантами оформления в `wireframe.html`
- [[block-composition]] — вставляет блок в `composed.html` с подстановкой design-tokens и текстов прототипа
- [[07a-wireframe]] — этап, на котором блок впервые используется

## Источник

- `block-library/gallery/gallery-minimal-grid-3-project21993216-tild-5/meta.yaml`
- Импортирован с [project21993216.tilda.ws](https://project21993216.tilda.ws/) методом `codex-block-generation` (2026-05-16)