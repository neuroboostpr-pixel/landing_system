---
type: block
name: process-technical-timeline-romanmelnikov-tilda-10
sources: ["block-library/process/process-technical-timeline-romanmelnikov-tilda-10/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["process", "timeline", "technical", "b2b", "horizontal", "ru-market"]
---

# Линейная схема этапов (технический таймлайн)

## Что делает
Показывает последовательность этапов работы в виде горизонтального таймлайна с мелкими подписями под каждым шагом. Визуально подчёркивает прогресс от начала к финалу — без анимаций, строго и по делу.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** агентом [[ux-composer]] при выборе блока категории `process` для ниш `services`, `b2b-saas` или `tech`. Подходит для лендингов с техническим/деловым стилем, где важна простота восприятия процесса работы. Блок собирается в [[block-composition]] на этапе 07b.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок секции (например: «Как мы работаем», «Этапы проекта»)
- `tokens.json` с дизайн-токенами (цвета, шрифты) — инжектируется автоматически на этапе 07b
- Прототипные тексты из `prototype.yaml` — подставляются вместо плейсхолдеров

**Выход:**
- HTML-блок с горизонтальным таймлайном, встроенный в `wireframe.html` (07a) или `composed.html` (07b)
- Нет анимаций (`has_animation: false`), нет фото-слотов — полностью текстовый блок

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe
- [[wireframe-rendering]] — рендерит блок в `wireframe.html` с CSS-вариантами
- [[block-composition]] — инжектирует токены и финальные тексты в `composed.html`
- [[block-library-management]] — управляет каталогом блоков, к которому принадлежит этот блок

## Источник
- `block-library/process/process-technical-timeline-romanmelnikov-tilda-10/meta.yaml`