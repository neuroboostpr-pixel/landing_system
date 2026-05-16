---
type: block
name: ru-process-03-4steps-numbered
sources: ["block-library/process/ru-process-03-4steps-numbered/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "ru_market", "b2c", "services", "local", "4steps", "grid", "opendesign"]
---

# Процесс — 4 шага в сетке с бордерами и иллюстрациями

## Что делает

Показывает клиенту путь к результату в виде четырёх пронумерованных шагов (01–04), расположенных в сетке с чёткими разделителями-бордерами. Каждая ячейка содержит иллюстрацию, акцентное число, заголовок и описание. Это создаёт ощущение чёткой структуры и надёжности — идеально для услуг.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — `ux-composer` выбирает этот блок из библиотеки, когда прототип описывает секцию «как мы работаем», «процесс сотрудничества» или «4 шага к результату». Подходит для сайтов услуг (B2C, local, сервисные компании). Особенно эффективен в связке со стилями Editorial & Magazine или Minimalism & Swiss.

Блок не подходит, если шагов меньше четырёх или контент не укладывается в ячейки с описаниями до 160 символов.

## Что на вход / на выход

**Слоты (вход от `content-writer` или прототипа):**

| Слот | Обязателен | Лимит |
|---|---|---|
| `kicker` | нет | 50 симв. |
| `headline` | **да** | 70 симв. |
| `subhead` | нет | 220 симв. |
| `step-1-title` … `step-4-title` | **да** × 4 | 40 симв. |
| `step-1-desc` … `step-4-desc` | **да** × 4 | 160 симв. |

Иллюстрации — автоматические **placeholder-слоты** (заполняются `visual-curator` на этапе 07d).

**Выход:**
- HTML-секция в `wireframe.html` (этап 07a) — сетка 4×1, mobile 2×2
- Затем — блок в `composed.html` (этап 07b) с реальными токенами и текстом

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — рендерит блок в composed.html с токенами дизайна
- [[wireframe-rendering]] — скилл этапа 07a, производит wireframe.html
- [[block-composition]] — скилл этапа 07b, инжектирует токены и тексты
- [[visual-curator]] — заполняет иллюстрации в placeholder-слоты блока
- [[block-library-management]] — скилл управления и обновления библиотеки блоков

## Источник

- `block-library/process/ru-process-03-4steps-numbered/meta.yaml`
- Стиль основан на open-design-landing (Apache-2.0): `github.com/nexu-io/open-design`