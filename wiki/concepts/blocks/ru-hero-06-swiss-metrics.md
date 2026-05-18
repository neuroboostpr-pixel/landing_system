---
type: block
name: ru-hero-06-swiss-metrics
sources: ["block-library/hero/ru-hero-06-swiss-metrics/meta.yaml"]
updated: 2026-05-13
triggers: []
stage: "07a, 07b"
uses:
  - ux-composer
  - block-composer
  - block-composition
  - wireframe-rendering
tags:
  - hero
  - ru-market
  - fintech
  - b2b
  - swiss-style
  - brutalism
  - minimalism
  - metrics
---

# Hero — Швейцарский + Цифры-метрики

## Что делает

Блок-герой в швейцарском стиле с акцентом на числовые показатели. Слева — тёмная колонка с логотипом и навигацией, в центре — крупный заголовок с лаймово-жёлтым акцентом, справа — 2–3 карточки с ключевыми цифрами (выручка, клиенты, опыт и т.п.). Подходит для финтех-компаний и B2B-сервисов, которым важно сразу показать экспертизу через данные.

## Когда вызывать / в каком этапе

Выбирается на этапе **07a (Wireframe)** в `ux-composer`, когда прототип содержит hero-секцию с числовыми метриками. Рекомендуется при стилях **Brutalism** или **Minimalism & Swiss Style**. Активен для ниш: финансы, SaaS, профессиональные услуги, B2B. На этапе **07b (Compose)** `block-composer` подставляет токены дизайна и тексты из `prototype.yaml`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — тексты для слотов (headline, subhead, метрики)
- `tokens.json` — цвета акцента (лайм/жёлтый), шрифты, отступы
- `selections.yaml` — подтверждённый выбор блока пользователем

**Слоты (обязательные):**
| Слот | Тип | Макс. символов |
|---|---|---|
| headline | text | 60 |
| subhead | text | 180 |
| metric-1-value | text | 12 |
| metric-1-label | text | 40 |
| metric-2-value | text | 12 |
| metric-2-label | text | 40 |
| primary-cta | cta | — |

**Слоты (необязательные):** metric-3-value, metric-3-label

**Выход:**
- HTML-фрагмент блока в `composed.html` с инжектированными токенами и текстами; визуальные photo-слоты отсутствуют (блок текстовый).

## Конверсионные заметки

Цифровые метрики работают как социальное доказательство и убеждают с первого экрана. Швейцарская сетка формирует восприятие надёжности и системности. Лаймовый/жёлтый акцент на CTA и подзаголовках усиливает кликабельность. Источник шаблона — OpenDesign (Apache-2.0, `digits-fintech-swiss-template`).

## Связанные концепты

- [[ux-composer]] — выбирает блок при формировании wireframe.html на этапе 07a
- [[block-composer]] — рендерит composed.html с подстановкой токенов на этапе 07b
- [[block-composition]] — скилл, управляющий логикой сборки блоков
- [[wireframe-rendering]] — скилл интерактивного wireframe с вариантами блоков
- [[design-tokens-generation]] — генерирует tokens.json, из которого берётся цвет акцента

## Источник

- `block-library/hero/ru-hero-06-swiss-metrics/meta.yaml`
- Оригинал: OpenDesign `/tmp/open-design/skills/digits-fintech-swiss-template/example.html` (Apache-2.0)