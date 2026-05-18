---
type: block
name: hero-cinematic-split-antidiler-karpov-ru-1
sources: ["block-library/hero/hero-cinematic-split-antidiler-karpov-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a, 07b"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "cinematic", "split", "premium-auto", "luxury", "ru-market"]
---

# Hero — Тёмный кинематографичный экран с наклонным заголовком (antidiler-karpov)

## Что делает

Первый экран (hero) в тёмном кинематографичном стиле: крупный наклонный заголовок поверх автомобильного фонового изображения, контрастная кнопка CTA. Макет типа «split» — текст и визуал чётко разделены. Анимаций нет — загружается мгновенно. Импортирован с сайта antidiler-karpov.ru как реальный пример из российского премиум-авто рынка.

## Когда вызывать / в каком этапе

- **Этап 07a (Wireframe):** `ux-composer` выбирает этот блок из библиотеки, если прототип требует тёмного hero-экрана для авто, luxury или services ниши. Блок отображается как один из 2–3 кандидатов в `wireframe.html`.
- **Этап 07b (Compose):** `block-composer` инжектирует дизайн-токены из `tokens.json` (цвета, шрифты) и подставляет текст из `prototype.yaml` вместо placeholder-контента. Результат — часть `composed.html`.

Подходит для ниш: `premium-auto`, `services`, `luxury`. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип `text`, обязательный) — главный заголовок первого экрана.
- Дизайн-токены из `tokens.json` (цвет акцента, шрифт заголовка).
- Фоновое изображение (фото автомобиля из `07c_PHOTOS/` или placeholder).

**Выход:**
- HTML-фрагмент блока: тёмный фон, наклонный `<h1>`, кнопка CTA с контрастным цветом.
- Встраивается в `wireframe.html` (этап 07a) и `composed.html` (этап 07b).

## Связанные концепты

- [[ux-composer]] — выбирает этот блок при сборке wireframe из библиотеки
- [[block-composer]] — рендерит финальный composed.html с инжектированными токенами
- [[wireframe-rendering]] — скилл, управляющий этапом 07a
- [[block-composition]] — скилл, управляющий этапом 07b
- [[block-library-management]] — описывает правила хранения и версионирования блоков в библиотеке

## Источник

- `block-library/hero/hero-cinematic-split-antidiler-karpov-ru-1/meta.yaml`