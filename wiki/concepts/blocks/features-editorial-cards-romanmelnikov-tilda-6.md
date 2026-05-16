---
type: block
name: features-editorial-cards-romanmelnikov-tilda-6
sources: ["block-library/features/features-editorial-cards-romanmelnikov-tilda-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["features", "editorial", "cards", "ru_market", "b2b-saas", "education", "services"]
---

# Секция features — редакционные карточки с контурами

## Что делает
Блок секции «Особенности» с большим дисплейным заголовком и набором карточек в контурном (outline) стиле. Подходит для акцента на ограниченных ресурсах, уникальных условиях или ключевых преимуществах продукта.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)**: агент [[ux-composer]] выбирает этот блок из библиотеки при формировании wireframe.html, если прототип содержит секцию с карточками в редакционном стиле. Ниши: `services`, `b2b-saas`, `education`. Анимация отсутствует — безопасен для строгих корпоративных проектов.

## Что на вход / на выход

**Вход:**
- Слот `heading` (обязательный, тип `text`) — главный дисплейный заголовок секции (например: «Только 12 мест в потоке»).
- Контент карточек поставляется через prototype.yaml на этапе [[07-prototip]].

**Выход:**
- HTML-блок с контурными карточками, встроенный в `wireframe.html` (этап 07a) и далее в `composed.html` (этап [[07b-composed]]).
- Стилизуется токенами из `tokens.json` после прохождения этапа [[05-dizayn-sistema]].

## Связанные концепты
- [[ux-composer]] — агент выбирает этот блок при сборке wireframe
- [[block-library-management]] — скилл управления библиотекой, хранит и индексирует блок
- [[wireframe-rendering]] — скилл рендера wireframe.html, вставляет блок в итоговый HTML
- [[block-composition]] — скилл этапа 07b, инжектирует design-tokens и тексты прототипа в блок
- [[07a-wireframe]] — этап, на котором блок впервые появляется в проекте
- [[07b-composed]] — этап финальной сборки с токенами и контентом

## Источник
- `block-library/features/features-editorial-cards-romanmelnikov-tilda-6/meta.yaml`