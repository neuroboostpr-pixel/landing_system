---
slug: moodboard-creation
type: skill
name: "Рендер мудборда"
stage: "03"
tags: [moodboard, references, html-render, jinja2]
triggers: [moodboard-composer]
inputs: [03_РЕФЕРЕНСЫ/index.yaml, 03_РЕФЕРЕНСЫ/moodboard.md]
outputs: [03_РЕФЕРЕНСЫ/moodboard.html]
gates: []
pre_reqs: [references-curator]
related: [moodboard-composer, references-curator, visual-curator]
sources: ["skills/moodboard-creation/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low, outputs: low}
---

# Рендер мудборда

## Что делает

Скилл читает файл `03_РЕФЕРЕНСЫ/index.yaml`, разделяет все референсы на одобренные (`approved`) и отклонённые (`rejected`), а затем рендерит HTML-страницу мудборда через шаблон Jinja2 (`moodboard.html.j2`). Если рядом лежит файл `moodboard.md` с нарративом (текстовым описанием вижн-направления), он встраивается прямо в HTML-превью. Точка входа в рендер — скрипт `scripts/render.py`.

## Когда вызывается

Вызывается агентом `moodboard-composer` после того, как куратор референсов (`references-curator`) разметил `index.yaml` — проставил статусы `approved`/`rejected` у каждого визуального референса этапа 03. Скилл не запускается без размеченного `index.yaml`.

## Вход → выход

**Вход:** `03_РЕФЕРЕНСЫ/index.yaml` с заполненными статусами референсов; опционально `03_РЕФЕРЕНСЫ/moodboard.md` с текстовым нарративом.

**Выход:** `moodboard.html` — готовая HTML-страница для просмотра и утверждения мудборда. Одобренные референсы отображаются, отклонённые скрыты или помечены.

## Failure modes

- `index.yaml` отсутствует или не содержит ни одного `approved`-референса — рендер создаёт пустую страницу без контента.
- Шаблон `moodboard.html.j2` не найден по ожидаемому пути — `render.py` падает с ошибкой и `moodboard.html` не создаётся.
- Некорректный YAML в `index.yaml` (синтаксическая ошибка) — парсер упадёт, скилл не выполнится.
- Нарратив из `moodboard.md` содержит непарный HTML или спецсимволы — встраивание в шаблон может нарушить разметку страницы.
- Путь запуска не из корня проекта лендинга — относительные пути в `render.py` не найдут исходники.

## Related

- [[moodboard-composer]] — агент-владелец скилла; он оркестрирует вызов и принимает результат
- [[references-curator]] — заполняет `index.yaml` статусами до запуска рендера
- [[visual-curator]] — смежная роль, занимается отбором визуальных материалов на том же этапе