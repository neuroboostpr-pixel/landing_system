---
type: block
name: footer-minimal-split-antidiler-karpov-ru-8
sources: ["block-library/footer/footer-minimal-split-antidiler-karpov-ru-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer"]
tags: ["footer", "minimal", "split", "ru-market", "premium-auto", "b2b-saas"]
---

# Footer: Низкая тёмная панель с юридическими ссылками

## Что делает

Отрисовывает тёмную узкую нижнюю полосу сайта, разделённую на две колонки (split): слева — название компании или короткий лозунг, справа — мелкие юридические и служебные ссылки (политика конфиденциальности, оферта, ИНН и т.п.). Никакой анимации, строго минималистичный стиль.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Compose)** при сборке `composed.html`. Агент [[block-composer]] выбирает этот блок, когда прототип предполагает лаконичный footer без навигационных колонок или крупных CTA. Подходит для проектов в нишах **premium-auto**, **services** и **b2b-saas**, ориентированных на российский рынок.

Также может быть подобран агентом [[ux-composer]] на этапе **07a (Wireframe)** в качестве кандидата для слота `footer`.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — короткая строка: название бренда, копирайт-строка или служебный идентификатор компании.

**Выход:**
- HTML-фрагмент тёмного footer-а с разделением на две зоны: брендовая и юридическая.
- Встраивается в `composed.html` как самостоятельный блок в конце страницы.

## Связанные концепты

- [[block-composer]] — использует блок при сборке composed.html на этапе 07b
- [[ux-composer]] — может выбрать блок как вариант на wireframe-этапе 07a
- [[block-library-management]] — скилл, управляющий реестром блоков, в котором зарегистрирован этот блок
- [[07b-composed]] — этап, на котором блок активно используется
- [[07a-wireframe]] — этап, на котором блок подбирается как кандидат

## Источник

- `block-library/footer/footer-minimal-split-antidiler-karpov-ru-8/meta.yaml`
- Импортировано с [antidiler-karpov.ru](https://antidiler-karpov.ru/) методом `codex-block-generation` 2026-05-16