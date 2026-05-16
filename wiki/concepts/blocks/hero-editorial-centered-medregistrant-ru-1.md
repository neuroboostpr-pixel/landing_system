---
type: block
name: hero-editorial-centered-medregistrant-ru-1
sources: ["block-library/hero/hero-editorial-centered-medregistrant-ru-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "editorial", "centered", "typography", "ru-market", "services", "medical", "education"]
---

# Hero Editorial Centered — крупный типографический первый экран

## Что делает

Отображает первый экран лендинга с крупной типографикой по центру, ручной иллюстрацией и акцентной кнопкой CTA. Визуально строгий редакционный стиль — без лишних деталей, вся сила в заголовке.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** и **07b (Compose)** как вариант блока `hero` для проектов в нишах услуг, медицины и образования. Агент [[ux-composer]] подбирает этот блок из библиотеки, если прототип задаёт centered-раскладку и editorial-настроение. [[block-composer]] инжектирует токены дизайна и подставляет текст прототипа в слот `heading`.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — главный заголовок первого экрана
- Токены дизайна из `tokens.json` (цвета, шрифты, радиусы кнопки)
- Контент из `prototype.yaml` (текст заголовка и CTA)

**Выход:**
- HTML-фрагмент hero-блока, готовый к встройке в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Placeholder для ручной иллюстрации (заполняется на этапе PR-B/PR-C)

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при формировании wireframe.html
- [[block-composer]] — инжектирует design-токены и тексты на этапе composed.html
- [[wireframe-rendering]] — скилл, управляющий рендером всех блоков в интерактивный wireframe
- [[block-composition]] — скилл compose-этапа, подставляет реальные тексты и токены
- [[block-library-management]] — скилл, управляющий каталогом блоков и импортом новых
- [[photo-curator]] — на этапе 07c заполняет слот иллюстрации реальным фото клиента

## Источник

- `block-library/hero/hero-editorial-centered-medregistrant-ru-1/meta.yaml`
- Импортировано с [medregistrant.ru](https://medregistrant.ru/) методом `codex-block-generation` (2026-05-16)