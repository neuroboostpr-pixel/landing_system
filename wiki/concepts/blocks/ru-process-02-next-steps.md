---
type: block
name: ru-process-02-next-steps
sources: ["block-library/process/ru-process-02-next-steps/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "timeline", "editorial", "ru_market", "b2c", "services", "local"]
---

# 📋 Процесс — 3 шага timeline-стиль

## Что делает

Показывает клиенту три шага сотрудничества в виде горизонтальной временно́й шкалы: каждый шаг — конкретный срок и действие. Последний шаг выделяется тёмной или акцентной карточкой, акцентируя итоговую выгоду. Снимает тревогу «сколько ждать» и ведёт к CTA.

## Когда вызывать / в каком этапе

Используется на этапе **07a (wireframe)** при подборе блоков для секции «Как мы работаем» / «Процесс». Подходит для услуг, B2C и локального бизнеса. Рекомендуется в стилях **Minimalism & Swiss Style** и **Editorial**. Агент [[ux-composer]] выбирает этот блок из библиотеки, если прототип содержит секцию с пошаговым процессом.

## Что на вход / на выход

**Вход (слоты):**

| Слот | Тип | Макс. символов | Обязателен |
|---|---|---|---|
| `headline` | text | 60 | ✅ |
| `step1-timing` | text | 20 | ✅ |
| `step1-title` | text | 50 | ✅ |
| `step1-text` | text | 200 | ✅ |
| `step2-timing` | text | 20 | ✅ |
| `step2-title` | text | 50 | ✅ |
| `step2-text` | text | 200 | ✅ |
| `step3-timing` | text | 20 | ✅ |
| `step3-title` | text | 50 | ✅ |
| `step3-text` | text | 200 | ✅ |
| `primary-cta` | cta | — | ✅ (default: «Начать») |

**Выход:** HTML-фрагмент блока с тремя строками-карточками, временны́ми метками и акцентным финальным шагом, готовый к инжекции в `wireframe.html` / `composed.html`.

## Конверсионные заметки

Временны́е метки (например, «День 1», «3 дня», «Через неделю») психологически снижают барьер входа — клиент понимает конкретные сроки. Финальный тёмно-акцентный шаг фиксирует итоговую выгоду. CTA расположен сразу после блока — максимально близко к моменту принятия решения.

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe.html
- [[block-composer]] — инжектирует токены и тексты при этапе 07b
- [[wireframe-rendering]] — скилл рендера интерактивного wireframe с блоком
- [[block-composition]] — скилл финальной сборки composed.html
- [[block-library-management]] — управление библиотекой, регистрация блока

## Источник

- `block-library/process/ru-process-02-next-steps/meta.yaml`
- Вдохновлён: OpenDesign / release-notes one-pager (`source_attribution: /tmp/open-design/skills/release-notes-one-pager/example.html`), лицензия Apache-2.0