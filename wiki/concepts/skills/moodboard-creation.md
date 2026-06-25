---
slug: moodboard-creation
type: skill
name: "Рендер мудборда"
stage: "03"
tags: [moodboard, references, render, html]
triggers: [landing-moodboard]
inputs: [03-referensy]
outputs: [03-referensy]
gates: []
pre_reqs: [03-referensy, references-collection]
related: [moodboard-composer, landing-moodboard, landing-references, references-curator, visual-curator]
sources: ["skills/moodboard-creation/SKILL.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Рендер мудборда

## Что делает

Скилл читает файл `03_РЕФЕРЕНСЫ/index.yaml`, в котором собраны визуальные референсы проекта, и делит их на одобренные (`approved`) и отклонённые (`rejected`). На основании одобренных он рендерит `moodboard.html` через шаблонизатор Jinja2 (шаблон `moodboard.html.j2`). Если рядом лежит нарративный файл `moodboard.md`, его содержимое встраивается в HTML-превью в виде пояснительного текста. Итог — готовая для демонстрации HTML-страница с коллажем референсов.

## Когда вызывается

Вызывается агентом `moodboard-composer` на этапе 03 (Референсы), как правило сразу после того, как маркетолог утвердил набор визуальных референсов и заполнил `index.yaml`. Внешняя точка входа — команда `/landing-moodboard`.

## Вход → выход

**Вход:** `03_РЕФЕРЕНСЫ/index.yaml` с размеченными статусами `approved`/`rejected`; опционально — `03_РЕФЕРЕНСЫ/moodboard.md` с текстовым нарративом.

**Выход:** `03_РЕФЕРЕНСЫ/moodboard.html` — отрендеренная HTML-страница для просмотра и утверждения клиентом/маркетологом.

## Failure modes

- `index.yaml` отсутствует или не содержит ни одного `approved` референса — рендер падает с пустым результатом.
- Шаблон `moodboard.html.j2` не найден или содержит синтаксическую ошибку Jinja2 — рендер прерывается без HTML-вывода.
- Ссылки на изображения в `index.yaml` битые или недоступны — превью рендерится, но с пустыми ячейками.
- `moodboard.md` существует, но повреждён (например, BOM или encoding issue) — нарратив тихо пропускается без предупреждения.
- Скрипт `scripts/render.py` не установлен или отсутствуют зависимости Python (Jinja2) — весь вызов завершается с ошибкой импорта.

## Related

- [[moodboard-composer]] — агент-владелец скилла, вызывает его напрямую
- [[landing-moodboard]] — slash-команда, являющаяся внешней точкой входа для этого скилла
- [[landing-references]] — команда сбора референсов, формирует `index.yaml` который читает данный скилл
- [[references-curator]] — куратор, расставляет статусы approved/rejected в index.yaml
- [[visual-curator]] — связан через общий контекст визуальных материалов этапа 03