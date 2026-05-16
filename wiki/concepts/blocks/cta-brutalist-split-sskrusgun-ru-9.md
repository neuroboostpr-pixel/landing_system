---
type: block
name: cta-brutalist-split-sskrusgun-ru-9
sources: ["block-library/cta/cta-brutalist-split-sskrusgun-ru-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composition", "ux-composer", "block-composer", "block-library-management"]
tags: ["cta", "brutalist", "split", "ru-market", "services", "education", "b2b-saas", "lead-magnet"]
---

# Яркий красный CTA — лид-магнит с фото и формой (brutalist split)

## Что делает
Блок призыва к действию в брутальном стиле: красный фон, фото людей слева, короткая форма захвата справа, контрастная чёрная кнопка. Подходит для быстрого сбора лидов на русскоязычном рынке.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — когда `ux-composer` подбирает блок CTA из библиотеки под wireframe, и `block-composer` вставляет его в `composed.html` с токенами дизайна и текстом из прототипа.

Подходящие ниши: **услуги (services), образование (education), B2B SaaS**. Ориентирован на ру-рынок (`ru_market: true`). Анимация отсутствует — подходит для проектов без GSAP.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок лид-магнита
- Токены дизайна из `tokens.json` (цвета, шрифты) — применяются при compose
- Фото людей — подставляется в фото-слот через pipeline PR-B (`07c_PHOTOS`)

**Выход:**
- HTML-фрагмент блока внутри `07b_COMPOSED/composed.html`
- Красный split-layout: фото-панель + форма с чёрной CTA-кнопкой

## Связанные концепты
- [[block-composition]] — скилл этапа 07b, который инжектирует токены и тексты в блок
- [[ux-composer]] — агент, выбирающий этот блок из библиотеки для wireframe
- [[block-composer]] — агент, рендерящий итоговый composed.html с блоком
- [[block-library-management]] — скилл управления каталогом блоков, куда входит этот блок
- [[photo-curator]] — обрабатывает фото людей для фото-слота блока (этап 07c)

## Источник
- `block-library/cta/cta-brutalist-split-sskrusgun-ru-9/meta.yaml`