---
type: block
name: trust-playful-stacked-opt-ecowash-ru-4
sources: ["block-library/trust/trust-playful-stacked-opt-ecowash-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-library-management"]
tags: ["trust", "playful", "stacked", "ru-market", "ecommerce", "services"]
---

# Яркий блок доверия — стопка с декоративной графикой

## Что делает
Отображает секцию доверия с крупным заголовком, несколькими метриками и большой декоративной графикой. Оформлен в ярком, игривом стиле — привлекает внимание и визуально усиливает ключевые числа или достижения компании.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Block Compose)** — `block-composer` и `ux-composer` выбирают этот блок из библиотеки, когда прототип содержит секцию социального доказательства или доверия. Подходит для ниш **ecommerce** и **services** на русскоязычном рынке. Рекомендуется, когда дизайн-мудборд задаёт настроение `playful` и компоновка идёт стопкой (`stacked`).

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — главный заголовок блока доверия
- Метрики / цифры (вставляются через слоты или токены из `tokens.json`)
- Декоративная графика (placeholder, заменяется на этапах PR-B или PR-C)

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html`
- Слоты для фото и инфографики помечаются как labeled placeholders до прохождения этапов 07c–07d

## Ограничения
- `has_animation: false` — анимация отключена; подключать GSAP не нужно
- Импортирован с [opt.ecowash.ru](https://opt.ecowash.ru/) методом `codex-block-generation` 2026-05-16; при редизайне сверяться с оригинальным источником

## Связанные концепты
- [[block-composer]] — вставляет блок в composed.html на этапе 07b
- [[ux-composer]] — выбирает блок при построении wireframe (07a)
- [[block-library-management]] — управляет каталогом блоков, включая этот
- [[block-composition]] — скилл, описывающий процесс сборки блоков с токенами
- [[07b-composed]] — этап, на котором блок впервые рендерится с реальным контентом

## Источник
- `block-library/trust/trust-playful-stacked-opt-ecowash-ru-4/meta.yaml`