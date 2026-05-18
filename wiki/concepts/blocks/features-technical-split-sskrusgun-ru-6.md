---
type: block
name: features-technical-split-sskrusgun-ru-6
sources: ["block-library/features/features-technical-split-sskrusgun-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-library-management"]
tags: ["features", "technical", "split", "services", "education", "ru-market"]
---

# Features Technical Split — Промо-карточка + список направлений

## Что делает

Блок типа «features» с раскладкой split: слева промо-карточка с заголовком, справа — список направлений работы и ссылки на разные форматы услуги. Подходит для технических и сервисных компаний, которым важно сразу показать спектр предложений.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** — агент [[ux-composer]] выбирает блок из библиотеки при сборке `wireframe.html`. Подходит когда прототип содержит секцию с перечислением нескольких направлений или форматов услуги (курсы, пакеты, консультации, тарифы). Ориентирован на **российский рынок** (`ru_market: true`).

Ниши: **services**, **education**.

## Что на вход / на выход

**Вход (обязательные слоты):**
| Слот | Тип | Обязательный |
|------|-----|--------------|
| `heading` | text | да |

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` или `composed.html`
- При прохождении этапа 07b ([[block-composition]]) — токены дизайна и текст-контент подставляются в слот `heading` из `prototype.yaml`

## Особенности

- **Анимация:** отсутствует (`has_animation: false`) — статичный блок, быстрая загрузка
- **Раскладка:** `split` — двухколоночная горизонтальная структура
- **Настроение:** `technical` — строгий, деловой визуальный стиль
- **Источник:** импортирован с `sskrusgun.ru` методом `codex-block-generation` (2026-05-16)

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe на этапе 07a
- [[wireframe-rendering]] — скилл, управляющий рендерингом wireframe.html с блоками из библиотеки
- [[block-composition]] — скилл этапа 07b: подставляет tokens + текст в слоты блока
- [[block-library-management]] — скилл управления пополнением и каталогом библиотеки
- [[prototype-importer]] — поставляет `prototype.yaml`, из которого берётся контент для слота `heading`

## Источник

- `block-library/features/features-technical-split-sskrusgun-ru-6/meta.yaml`