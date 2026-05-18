---
type: block
name: features-editorial-grid-2-romanmelnikov-tilda-9
sources: ["block-library/features/features-editorial-grid-2-romanmelnikov-tilda-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["features", "editorial", "grid-2", "risks", "ru-market", "b2b-saas", "services", "education"]
---

# Секция рисков — Editorial Grid 2 (romanmelnikov / Tilda)

## Что делает
Отображает секцию «Риски» с гигантским заголовком, одной контурной карточкой и несколькими поясняющими колонками текста. Визуальный стиль — editorial: крупная типографика, строгая сетка, без анимации.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)**: агент [[ux-composer]] выбирает этот блок из библиотеки при наличии секции «Риски» или «Возражения» в `prototype.yaml`. Подходит для посадочных страниц в нишах **B2B-услуги**, **B2B-SaaS** и **Образование**, ориентированных на российский рынок.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — блок секции с контентом раздела рисков/возражений
- Обязательный слот `heading` (тип: text) — заголовок секции

**Выход:**
- HTML-фрагмент блока, встроенный в `07a_WIREFRAME/wireframe.html` (через [[wireframe-rendering]])
- При переходе на этап 07b — фрагмент попадает в `07b_COMPOSED/composed.html` (через [[block-composition]])

## Дополнительные характеристики
| Параметр | Значение |
|---|---|
| Категория | features |
| Паттерн раскладки | grid-2 |
| Стиль | editorial |
| Анимация | нет |
| Рынок | ru_market |
| Источник | romanmelnikov.tilda.ws |
| Метод импорта | codex-block-generation |

## Связанные концепты
- [[ux-composer]] — агент, который выбирает блок из библиотеки при составлении wireframe
- [[block-library-management]] — скилл управления библиотекой; отвечает за регистрацию и поиск блока
- [[wireframe-rendering]] — скилл, рендерящий wireframe.html с данным блоком
- [[block-composition]] — скилл этапа 07b, инжектирующий токены и прототипный текст в блок
- [[07a-wireframe]] — этап, где блок впервые появляется в проекте

## Источник
- `block-library/features/features-editorial-grid-2-romanmelnikov-tilda-9/meta.yaml`