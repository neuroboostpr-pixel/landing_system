---
type: block
name: cta-corporate-split-project21993216-tild-6
sources: ["block-library/cta/cta-corporate-split-project21993216-tild-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "corporate", "split", "b2b-saas", "services", "ecommerce", "ru-market"]
---

# CTA Corporate Split — горизонтальный баннер с оффером и кнопкой справа

## Что делает

Горизонтальный CTA-баннер в корпоративном стиле: слева — короткий оффер и поясняющий текст, справа — кнопка призыва к действию. Подходит для бизнес-лендингов, где нужно ненавязчиво, но чётко направить посетителя к следующему шагу.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при подборе CTA-блока. Подходит для проектов в нишах **B2B SaaS**, **услуги** и **e-commerce**, ориентированных на русскоязычный рынок. Выбирается агентом [[ux-composer]] из библиотеки блоков при компоновке wireframe, затем задействуется [[block-composer]] на этапе 07b.

## Что на вход / на выход

**Вход:**
- Слот `heading` (текст, обязательный) — короткий оффер/заголовок баннера.
- Дизайн-токены из `tokens.json` (цвета, типографика) — подставляются на этапе 07b.
- Прототипный текст из `prototype.yaml` — заменяет placeholder-копию.

**Выход:**
- HTML-фрагмент блока в составе `wireframe.html` (этап 07a) или `composed.html` (этап 07b).
- Блок без анимации (`has_animation: false`) — статичный, лёгкий.

## Характеристики блока

| Параметр | Значение |
|---|---|
| Категория | `cta` |
| Layout | `split` (горизонтальный) |
| Настроение | `corporate` |
| Анимация | нет |
| Рынок | ru_market |
| Импортирован из | [project21993216.tilda.ws](https://project21993216.tilda.ws/) |

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — инжектирует токены и текст в блок на этапе 07b
- [[wireframe-rendering]] — скилл рендеринга wireframe.html, куда входит блок
- [[block-composition]] — скилл финальной сборки composed.html
- [[block-library-management]] — управление библиотекой, откуда взят блок

## Источник

- `block-library/cta/cta-corporate-split-project21993216-tild-6/meta.yaml`