---
type: block
name: gallery-cinematic-cards-zilant-group-3
sources: ["block-library/gallery/gallery-cinematic-cards-zilant-group-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition", "block-library-management"]
tags: ["gallery", "cinematic", "cards", "premium-auto", "luxury", "real-estate", "services", "animation", "ru-market"]
---

# Gallery Cinematic Cards — Zilant Group 3

## Что делает
Отображает секцию с крупным заголовком и тремя тёмными фотокарточками услуг с короткими подписями. Визуальный стиль — кинематографичный (тёмные тона, выразительная типографика, анимация при появлении).

## Когда вызывать / в каком этапе
Используется на этапе **07b (Block Compose)** при сборке `composed.html`. Агент [[ux-composer]] выбирает этот блок из библиотеки на этапе 07a (wireframe), если прототип содержит секцию-галерею или «наши услуги» в стиле premium/luxury. Агент [[block-composer]] подставляет реальные тексты и токены дизайна.

Подходит для ниш: **услуги, премиальный авто, люкс, недвижимость**. Ориентирован на русскоязычный рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `heading` — текстовый слот (обязательный): крупный заголовок секции
- Токены дизайна из `tokens.json` (цвета, шрифты) — подставляются агентом [[block-composer]]
- Фотографии для карточек — заполняются на этапе **07c** агентом [[photo-curator]] (слоты типа `photo` отсутствуют в meta, но визуально подразумеваются тёмными фотофонами карточек)

**Выход:**
- HTML-блок, встроенный в `07b_COMPOSED/composed.html`
- Анимация активируется через CSS/JS (has_animation: true)

## Связанные концепты
- [[block-composer]] — рендерит блок в composed.html на этапе 07b, подставляет тексты и токены
- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe на этапе 07a
- [[block-composition]] — скилл, управляющий логикой сборки блоков
- [[block-library-management]] — скилл учёта и импорта блоков в библиотеку
- [[photo-curator]] — заполняет фотографии в карточках на этапе 07c
- [[07b-composed]] — этап, в котором блок используется

## Источник
- `block-library/gallery/gallery-cinematic-cards-zilant-group-3/meta.yaml`
- Импортирован с: `https://zilant.group/` (2026-05-16, метод: codex-block-generation)