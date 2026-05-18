---
type: block
name: features-brutalist-grid-3-portfolio-kdm1-ru-3
sources: ["block-library/features/features-brutalist-grid-3-portfolio-kdm1-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "brutalist", "grid-3", "ru-market", "services", "ecommerce", "b2b-saas", "tech"]
---

# Features — Брутальная сетка карточек с типографским заголовком

## Что делает
Блок «Features» в брутальном стиле: крупный типографский заголовок, портретное фото и сетка из трёх карточек для разных сегментов аудитории или продуктовых направлений. Подходит для сервисных, B2B и e-commerce лендингов на русском рынке.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** — `ux-composer` выбирает блок из библиотеки при формировании wireframe.html. Затем на этапе **07b (Compose)** — `block-composer` инжектирует токены дизайна и подставляет тексты из prototype.yaml в слоты блока. Блок выбирается автоматически если прототип содержит секцию «для кого» или «сегменты», а стиль проекта определён как brutalist.

## Что на вход / на выход

**На вход:**
- `heading` (text, обязательный) — большой типографский заголовок раздела
- Портретное фото (фото-слот, заполняется на этапе 07c через `photo-curator`)
- Тексты карточек из `prototype.yaml` (подставляются автоматически на 07b)
- `tokens.json` с цветами и шрифтами бренда (инжектируется `block-composer`)

**На выход:**
- HTML-фрагмент блока внутри `wireframe.html` (07a)
- Готовый HTML-фрагмент с токенами и текстами в `composed.html` (07b)

**Ограничения:**
- `has_animation: false` — CSS-анимации отсутствуют
- Адаптирован только для **российского рынка** (`ru_market: true`)
- Без портретного фото блок показывает labeled placeholder до этапа 07c

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe.html
- [[block-composer]] — рендерит composed.html, инжектирует токены и тексты в слоты
- [[wireframe-rendering]] — скилл, управляющий рендером wireframe на этапе 07a
- [[block-composition]] — скилл этапа 07b, собирает composed.html из выбранных блоков
- [[photo-curator]] — заполняет портретный фото-слот на этапе 07c
- [[block-library-management]] — скилл управления общей библиотекой блоков

## Источник
- `block-library/features/features-brutalist-grid-3-portfolio-kdm1-ru-3/meta.yaml`
- Импортирован из: `https://portfolio.kdm1.ru/upload/iblock/c4c/.../Spetsodezhda-Siti.pdf`
- Метод импорта: `codex-block-generation`, дата: 2026-05-16