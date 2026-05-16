---
type: block
name: cta-corporate-split-project21993216-tild-13
sources: ["block-library/cta/cta-corporate-split-project21993216-tild-13/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["cta", "form", "corporate", "split", "ru-market", "services", "b2b-saas", "ecommerce"]
---

# CTA Corporate Split — финальная форма заявки (split-макет)

## Что делает
Блок финального призыва к действию: левая половина содержит заголовок и убеждающий текст, правая — поля ввода формы и широкая яркая кнопка отправки. Корпоративный стиль без анимации, адаптирован под российский рынок.

## Когда вызывать / в каком этапе
Используется на этапе **07b (block-compose)** при сборке `composed.html`. Агент [[ux-composer]] подбирает блок на этапе 07a (wireframe), [[block-composer]] финально рендерит его с токенами дизайна и текстами из прототипа. Подходит для лендингов сервисного бизнеса, B2B-SaaS и ecommerce, когда нужна финальная конверсионная секция с формой заявки.

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип: text) — заголовок секции с призывом к действию
- Токены дизайна из `tokens.json` (цвета кнопки, типографика)
- Текстовый контент из `prototype.yaml`

**Выход:**
- HTML-фрагмент блока, встроенный в `07b_COMPOSED/composed.html`
- Визуально: split-макет (50/50), текст слева, форма справа, кнопка на полную ширину правой колонки

## Связанные концепты
- [[block-composer]] — рендерит блок в composed.html с инъекцией токенов и текстов
- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe
- [[block-composition]] — скилл, управляющий сборкой всех блоков на этапе 07b
- [[block-library-management]] — скилл управления каталогом блоков, куда входит этот блок
- [[07b-composed]] — этап pipeline, в котором блок применяется

## Источник
- `block-library/cta/cta-corporate-split-project21993216-tild-13/meta.yaml`