---
type: block
name: ru-quiz-02-progress-top
sources: ["block-library/quiz/ru-quiz-02-progress-top/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["quiz", "progress", "ru-market", "css-only", "b2c", "services", "local"]
---

# Квиз — вопрос с прогрессом сверху

## Что делает

Отображает шаг квиза с липким (sticky) прогресс-баром вверху страницы: текст «Шаг N из M» + CSS-полоска прогресса. Ниже — вопрос по центру и варианты ответа в две колонки. Без JavaScript — вся логика отображения на чистом CSS.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при сборке квиза для сервисных и B2C лендингов на русском рынке. Подходит для локальных бизнесов (услуги, B2C). Выбирается в `ux-composer` из block-library, когда в прототипе есть шаги квиза. Уместен на втором и последующих шагах квиза — там, где пользователь уже начал и важно удержать его до конца.

## Что на вход / на выход

**Входные слоты:**

| Слот | Тип | Обязателен | Ограничение |
|---|---|---|---|
| `progress-text` | text | ✅ да | до 20 символов |
| `progress-bar` | text | нет | CSS inline-style ширина |

**На выход:** HTML-блок с sticky progress bar, заголовком вопроса и вариантами ответа в 2 колонки. Ширина полоски задаётся через inline `style` — никакого JS.

**Conversion notes:** Прогресс-бар снижает отказы на 20–35%. Sticky-позиция гарантирует, что пользователь всегда видит, сколько шагов осталось.

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — инжектирует дизайн-токены и финальные тексты в блок на этапе 07b
- [[wireframe-rendering]] — рендерит интерактивный wireframe.html с этим блоком в составе квиза
- [[block-composition]] — этап 07b: подставляет реальный прогресс-текст вместо placeholder
- [[block-library-management]] — управляет реестром блоков, включая этот

## Источник

- `block-library/quiz/ru-quiz-02-progress-top/meta.yaml`