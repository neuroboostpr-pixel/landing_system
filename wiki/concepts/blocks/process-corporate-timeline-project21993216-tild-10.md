---
type: block
name: process-corporate-timeline
sources: ["block-library/process/process-corporate-timeline-project21993216-tild-10/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "timeline", "corporate", "b2b", "services", "education"]
---

# Process Corporate Timeline — Пошаговая схема с нумерованными карточками

## Что делает

Отображает последовательность шагов в виде нумерованных карточек по горизонтали или вертикали. Последняя карточка содержит кнопку призыва к действию. Подходит для объяснения «как мы работаем» или «как начать сотрудничество».

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** и **07b (Compose)**. Агент [[ux-composer]] выбирает этот блок из библиотеки, когда прототип содержит раздел «процесс работы», «шаги», «как это происходит» или аналог. Блок подходит для корпоративного сайта, B2B-сервиса, образовательного продукта или компании из сферы услуг.

Целевые ниши: `services`, `education`, `b2b-saas`.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок раздела, например «Как мы начинаем работу»
- Описания каждого шага (через контент прототипа)

**Выход:**
- HTML-блок с нумерованными карточками в паттерне `timeline`
- Финальная карточка с кнопкой CTA
- Вставляется в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)

**Параметры блока:**
- `style_mood`: corporate — строгий деловой стиль без излишеств
- `layout_pattern`: timeline — горизонтальная или вертикальная шкала шагов
- `has_animation`: false — без анимаций (подходит для консервативных заказчиков)
- `ru_market`: true — адаптирован под российский рынок

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe.html из prototype.yaml
- [[block-composer]] — инжектирует design-tokens и подставляет текст из прототипа при формировании composed.html
- [[wireframe-rendering]] — скилл, который рендерит интерактивный wireframe с этим блоком
- [[block-composition]] — скилл этапа 07b, собирает финальный composed.html
- [[block-library-management]] — скилл управления библиотекой блоков, из которой взят этот блок

## Источник

- `block-library/process/process-corporate-timeline-project21993216-tild-10/meta.yaml`
- Импортирован с `https://project21993216.tilda.ws/` методом `codex-block-generation` (2026-05-16)