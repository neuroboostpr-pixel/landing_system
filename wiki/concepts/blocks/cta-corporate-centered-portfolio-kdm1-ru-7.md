---
type: block
name: cta-corporate-centered-portfolio-kdm1-ru-7
sources: ["block-library/cta/cta-corporate-centered-portfolio-kdm1-ru-7/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["cta", "corporate", "centered", "ru-market", "services", "ecommerce", "b2b-saas"]
---

# Финальный CTA с центрированным заголовком и формой заявки

## Что делает
Завершающий блок лендинга: крупный центрированный заголовок, форма заявки и декоративная линейка персонажей снизу. Создаёт корпоративный финальный призыв к действию с чёткой визуальной точкой.

## Когда вызывать / в каком этапе
Используется на этапе **07b (block-composition / Compose)** — когда `block-composer` собирает `composed.html` из одобренных wireframe-вариантов. Подходит для ниш: услуги, ecommerce, b2b-saas. Блок ориентирован на российский рынок (`ru_market: true`). Анимации отсутствуют (`has_animation: false`) — подходит для строгого корпоративного стиля.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок CTA-секции.
- Токены дизайна из `tokens.json` (цвета, шрифты, отступы) — инжектируются автоматически при compose.
- Прототипный текст из `prototype.yaml` — подставляется вместо плейсхолдеров.

**Выход:**
- HTML-фрагмент блока, встраиваемый в `07b_COMPOSED/composed.html`.
- Декоративная линейка персонажей снизу (статичная, без анимации).

## Связанные концепты
- [[block-composer]] — агент, который выбирает блок и встраивает его в composed.html
- [[block-composition]] — скилл этапа 07b, управляет сборкой блоков с токенами и текстом
- [[ux-composer]] — агент этапа 07a, предлагает этот блок как кандидата в wireframe
- [[block-library-management]] — скилл управления библиотекой, регистрирует блок
- [[07b-composed]] — этап pipeline, в котором блок активно используется

## Источник
- `block-library/cta/cta-corporate-centered-portfolio-kdm1-ru-7/meta.yaml`