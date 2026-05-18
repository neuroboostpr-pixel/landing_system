---
type: block
name: cta-corporate-stacked-romanmelnikov-tilda-13
sources: ["block-library/cta/cta-corporate-stacked-romanmelnikov-tilda-13/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "corporate", "stacked", "ru-market", "services", "b2b-saas", "education"]
---

# Финальный призыв с крупным текстом, контактной строкой и компактной формой в рамке

## Что делает

Блок завершающего призыва к действию (CTA) в корпоративном стиле: крупный заголовок занимает всю ширину, под ним — строка с контактными данными, а рядом — компактная форма заявки в рамке. Всё выстроено в стопку (stacked), без анимаций — строго и делово.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** — `ux-composer` выбирает блок из библиотеки при сборке wireframe.html. Затем на этапе **07b (Compose)** — `block-composer` подставляет реальные тексты и токены дизайна. Подходит для проектов в нишах: услуги (`services`), B2B SaaS (`b2b-saas`), образование (`education`). Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (текст, обязательный) — крупный заголовок финального призыва
- Токены дизайна из `tokens.json` (цвета, типографика корпоративного стиля)
- Контактные данные и текст кнопки из `prototype.yaml`

**Выход:**
- HTML-фрагмент блока CTA, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Layout: вертикальный стек — заголовок → контакты → форма в рамке

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe по prototype.yaml
- [[block-composer]] — рендерит composed.html, подставляя реальные тексты и дизайн-токены в слот heading
- [[wireframe-rendering]] — скилл, запускающий интерактивный wireframe.html; именно здесь блок появляется как вариант для выбора
- [[block-composition]] — скилл этапа 07b, финализирующий блок с токенами и текстом прототипа
- [[block-library-management]] — управление всей библиотекой; этот блок — один из элементов коллекции cta

## Источник

- `block-library/cta/cta-corporate-stacked-romanmelnikov-tilda-13/meta.yaml`