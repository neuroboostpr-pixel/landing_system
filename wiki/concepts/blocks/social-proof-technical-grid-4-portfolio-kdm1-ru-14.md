---
type: block
name: social-proof-technical-grid-4-portfolio-kdm1-ru-14
sources: ["block-library/social-proof/social-proof-technical-grid-4-portfolio-kdm1-ru-14/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composition", "ux-composer", "block-composer"]
tags: ["social-proof", "grid-4", "technical", "ru-market", "statistics", "b2b"]
---

# Статистический блок — тёмная инфографичная подача (grid-4)

## Что делает
Отображает ключевые числовые показатели бизнеса (проценты, цифры) крупным шрифтом на тёмном фоне с короткими поясняющими подписями. Четыре ячейки в сетке создают ощущение технической весомости и доверия к данным.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — агент [[block-composer]] вставляет блок в `composed.html` после того, как в `07a_WIREFRAME/selections.yaml` выбран этот вариант блока категории `social-proof`. Подходит для проектов в нишах **услуги, образование, b2b-saas, tech**, где важно показать конкретные результаты цифрами.

## Что на вход / на выход

**На вход:**
- Слот `heading` (text, обязательный) — заголовок секции со статистикой
- Дизайн-токены из `tokens.json` (цвета, типографика) — инжектируются автоматически
- Контент из `prototype.yaml` — подставляется вместо плейсхолдеров

**На выход:**
- HTML-фрагмент блока внутри `07b_COMPOSED/composed.html`
- Тёмный фон, крупные числа/проценты, четыре колонки (grid-4), без анимаций (`has_animation: false`)

## Связанные концепты
- [[block-composer]] — агент, который рендерит `composed.html` и вставляет этот блок
- [[block-composition]] — скилл, описывающий логику сборки блоков с токенами
- [[ux-composer]] — агент 07a, который предлагает этот блок как вариант для wireframe
- [[07b-composed]] — этап пайплайна, где блок финально собирается
- [[design-tokens-generation]] — поставляет токены (цвета, шрифты), используемые блоком

## Источник
- `block-library/social-proof/social-proof-technical-grid-4-portfolio-kdm1-ru-14/meta.yaml`