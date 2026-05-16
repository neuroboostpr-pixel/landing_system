---
type: block
name: features-brutalist-split-antidiler-karpov-ru-2
sources: ["block-library/features/features-brutalist-split-antidiler-karpov-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["features", "brutalist", "split", "dark", "premium-auto", "services", "tech", "ru-market"]
---

# Короткий тёмный блок с крупным заявлением и зелёной акцентной плашкой преимущества

## Что делает

Блок секции «Преимущества» в брутальном стиле: тёмный фон, крупный заголовок-заявление слева и зелёная акцентная плашка с ключевым преимуществом справа. Визуально лаконичен и агрессивен — мгновенно считывается как «сильное УТП».

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — агент `ux-composer` выбирает этот блок из библиотеки при построении wireframe.html, если прототип содержит раздел преимуществ с брутальным или тёмным стилем. Подходит для ниш `premium-auto`, `services`, `tech`. Активируется через `/landing-wireframe`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` с описанием секции преимуществ
- `tokens.json` с дизайн-токенами проекта (цвета, шрифты)
- Слот `heading` (обязательный текст-заявление)

**Выход:**
- HTML-блок внутри `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Тёмный split-лейаут: заголовок слева + зелёная плашка с преимуществом справа
- Анимации отсутствуют (`has_animation: false`)

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html
- [[block-composition]] — инжектирует design-tokens и подставляет текст из prototype.yaml в composed.html
- [[wireframe-rendering]] — скилл этапа 07a, управляет сборкой блоков в интерактивный wireframe
- [[block-library-management]] — отвечает за импорт, хранение и обновление блоков библиотеки
- [[07a-wireframe]] — этап pipeline, где блок впервые появляется в сборке

## Источник

- `block-library/features/features-brutalist-split-antidiler-karpov-ru-2/meta.yaml`