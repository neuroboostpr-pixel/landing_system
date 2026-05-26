---
type: block
name: cta-corporate-stacked-romanmelnikov-tilda-13
sources: ["block-library/cta/cta-corporate-stacked-romanmelnikov-tilda-13/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["cta", "corporate", "stacked", "b2b", "services", "education", "ru-market"]
---

# Финальный призыв с крупным текстом и компактной формой в рамке

## Что делает
Блок завершения страницы: крупный заголовок-призыв, строка с контактами и компактная форма заявки в рамке — всё в деловом корпоративном стиле. Побуждает посетителя оставить заявку в самом конце лендинга.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** и **08 (Build)** как финальный CTA-блок страницы. Подходит для лендингов в нишах услуг, B2B-SaaS и образования, ориентированных на российский рынок. Выбирается вручную через wireframe.html или orchestrator'ом при подборе блоков категории `cta`.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — крупный заголовок-призыв к действию.
- Контактная строка и параметры формы подставляются из `tokens.json` и brand-kit проекта.

**Выход:**
- Готовый HTML-фрагмент блока, встроенный в `composed.html` или WordPress Lazy Block.
- Без анимаций (`has_animation: false`) — статичный, быстро грузится.

## Технические характеристики

| Параметр | Значение |
|---|---|
| Категория | `cta` |
| Раскладка | `stacked` (элементы друг под другом) |
| Настроение | `corporate` |
| Анимация | нет |
| Рынок | Россия (`ru_market: true`) |
| Источник | romanmelnikov.tilda.ws, импорт 2026-05-16 |
| Метод импорта | codex-block-generation |

## Связанные концепты
- [[landing-compose]] — этап 07b, на котором блок вставляется в composed.html
- [[landing-wireframe]] — этап 07a, на котором пользователь выбирает вариант CTA-блока
- [[landing-build]] — этап 08, где блок компилируется в Lazy Block для WordPress

## Источник
- `block-library/cta/cta-corporate-stacked-romanmelnikov-tilda-13/meta.yaml`