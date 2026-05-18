---
type: block
name: process-technical-stacked-opt-ecowash-ru-6
sources: ["block-library/process/process-technical-stacked-opt-ecowash-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition", "wireframe-rendering"]
tags: ["process", "technical", "stacked", "ru-market", "ecommerce", "services", "tech"]
---

# Производственный блок — technical stacked (ecowash)

## Что делает

Показывает производственный / технологический процесс: крупный заголовок, акцентная текстовая плашка, декоративная графика и большой медиаконтейнер (фото или видео). Подходит для страниц, где важно объяснить, «как это работает» или «из чего состоит услуга».

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** и **07a (Wireframe)**. `ux-composer` выбирает блок из библиотеки, когда прототип содержит секцию процесса/технологии. `block-composer` подставляет токены и тексты при финальной сборке `composed.html`. Подходит для ниш **ecommerce**, **services**, **tech** на российском рынке (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — секция с описанием процесса (заголовок обязателен, слот `heading`)
- `tokens.json` — цвета и типографика бренда
- Медиаконтент: фото или видео для большого медиаконтейнера (может быть placeholder)

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html`
- Слот `heading` заполнен текстом из прототипа; медиаконтейнер — либо реальное фото (после этапа 07c), либо labeled placeholder

## Особенности

- **Анимации нет** (`has_animation: false`) — блок статичный, без GSAP-эффектов
- **Раскладка stacked** — элементы расположены друг над другом по вертикали
- **Настроение technical** — строгий, деловой визуальный стиль
- Импортирован с `opt.ecowash.ru` методом `codex-block-generation` (16 мая 2026)
- Обязательный слот только один: `heading` (тип `text`)

## Связанные концепты

- [[block-composer]] — агент, который рендерит composed.html с этим блоком на этапе 07b
- [[ux-composer]] — агент, выбирающий блок в wireframe.html на этапе 07a
- [[block-composition]] — скилл, описывающий логику подстановки токенов и текстов
- [[wireframe-rendering]] — скилл рендеринга интерактивного wireframe с вариантами блоков
- [[block-library-management]] — скилл управления всей библиотекой блоков

## Источник

- `block-library/process/process-technical-stacked-opt-ecowash-ru-6/meta.yaml`