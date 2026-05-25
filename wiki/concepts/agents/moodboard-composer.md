---
type: agent
name: moodboard-composer
sources: ["agents/moodboard-composer.md"]
updated: 2026-05-25
triggers: []
stage: "03"
uses: ["landing-orchestrator", "stage-execution-protocol", "niche-analysis", "landing-references"]
tags: ["moodboard", "references", "visual-direction", "stage-03"]
---

# Moodboard Composer — сборщик мудборда

## Что делает

Берёт утверждённые референсы проекта и собирает из них две вещи: текстовое описание визуального направления (`moodboard.md`) и красивую HTML-страницу с карточками референсов (`moodboard.html`). Это итог этапа 03 — основа для бренд-кита и дизайн-системы.

## Когда вызывать / в каком этапе

Запускается автоматически агентом `landing-orchestrator` на этапе **03_references**, после того как пользователь утвердил набор референсов в `03_РЕФЕРЕНСЫ/index.yaml`. До запуска обязательно:
- `.landing-state.yaml` содержит `current_stage == 03_references`
- `gate-check.sh` для этапа возвращает exit 0

После формирования `moodboard.html` — **HARD GATE**: пользователь открывает файл в браузере и явно подтверждает направление. Только после этого `style-extractor` переходит к следующему этапу.

## Что на вход / на выход

**Вход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список референсов со статусом `approved`
- `01a_АНАЛИЗ_НИШИ/niche-analysis.md` — секция 6 «Что брать с собой» задаёт допустимый визуальный язык
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — секции 1–3, 5–6 определяют требования; referesы из red flag — не брать

**Выход:**
- `03_РЕФЕРЕНСЫ/moodboard.md` — текстовый нарратив: палитра, типографика, motion-вайб, что берём / что отвергаем
- `03_РЕФЕРЕНСЫ/moodboard.html` — визуальная доска с карточками референсов, открывается в браузере

## Как работает

1. Читает `index.yaml`, отбирает только `approved`-референсы.
2. Запрашивает у пользователя теги для каждого референса (например, `split-screen`, `warm-palette`, `premium-typography`).
3. Пишет `moodboard.md` с описанием выбранного направления.
4. Вызывает `python3 skills/moodboard-creation/scripts/render.py <refs-dir>` — генерирует `moodboard.html`.
5. Ждёт явного подтверждения от пользователя, только потом закрывает gate.

## Связанные концепты

- [[landing-orchestrator]] — вызывает агента в нужный момент pipeline
- [[stage-execution-protocol]] — обязательный протокол: state.yaml → Mermaid-карта → TodoWrite → gate-check перед любым Write/Edit
- [[landing-references]] — предыдущий этап, формирует `index.yaml` с утверждёнными референсами
- [[niche-analysis]] — `visual-requirements.md` определяет допустимые и запрещённые визуальные решения

## Источник

- `agents/moodboard-composer.md`