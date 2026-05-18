---
type: block
name: features-corporate-split-sskrusgun-ru-8
sources: ["block-library/features/features-corporate-split-sskrusgun-ru-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "split", "corporate", "checklist", "b2b", "ru-market"]
---

# Двухколоночный блок преимуществ (corporate-split)

## Что делает
Блок раздела «Преимущества» с разбивкой на две колонки: слева — текстовый чек-лист выгод корпоративного предложения, справа — интерьерное фото. Подходит для B2B-услуг, образовательных продуктов и SaaS-сервисов на русском рынке.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** при подборе блоков из библиотеки. `ux-composer` выбирает этот блок, когда в `prototype.yaml` обнаружена секция с перечнем корпоративных преимуществ и фото-сопровождением. Также задействуется на этапе **07b (Compose)** агентом `block-composer` при финальной сборке `composed.html`.

Настроение стиля — **corporate**, паттерн компоновки — **split** (горизонтальное разделение контента и визуала).

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип: text) — заголовок блока
- Интерьерное фото (фото-слот, заполняется на этапе 07c через `photo-curator`)
- Чек-лист преимуществ (текстовый контент из `prototype.yaml`)

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (07a) и `composed.html` (07b)
- Блок помечается как `ru_market: true` — оптимизирован под русскоязычную аудиторию

## Связанные концепты
- [[ux-composer]] — выбирает блок при рендеринге wireframe.html по prototype.yaml
- [[block-composer]] — встраивает блок в composed.html с токенами дизайна
- [[wireframe-rendering]] — скилл, управляющий выбором блоков из библиотеки
- [[block-composition]] — скилл финальной сборки с подстановкой контента
- [[photo-curator]] — заполняет фото-слот интерьерного снимка на этапе 07c
- [[block-library-management]] — управляет каталогом, откуда импортирован блок

## Источник
- `block-library/features/features-corporate-split-sskrusgun-ru-8/meta.yaml`