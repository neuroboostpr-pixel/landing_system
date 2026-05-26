---
type: agent
name: moodboard-composer
sources: ["agents/moodboard-composer.md"]
updated: 2026-05-26
triggers: []
stage: "03"
uses: ["landing-orchestrator", "stage-execution-protocol", "moodboard-creation"]
tags: ["moodboard", "references", "visual-direction", "stage-03"]
---

# Moodboard Composer

## Что делает
Агент собирает визуальный мудборд проекта: создаёт текстовое описание выбранного визуального направления (`moodboard.md`) и красивую HTML-страницу с карточками референсов (`moodboard.html`).

## Когда вызывать / в каком этапе
Запускается на **этапе 03 (референсы)**, после того как пользователь утвердил список визуальных референсов (статус `approved` в `index.yaml`). Является частью pipeline между анализом ниши и созданием бренд-кита.

## Что на вход / на выход

**Вход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список одобренных референсов с тегами
- `01a_АНАЛИЗ_НИШИ/niche-analysis.md` — секция 6 с визуальным языком ниши
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — визуальные требования (секции 1, 2, 3, 5, 6)
- `.landing-state.yaml` — должен показывать `current_stage == 03_references`

**Выход:**
- `03_РЕФЕРЕНСЫ/moodboard.md` — текстовый нарратив: палитра, типографика, анимация, что берём и отвергаем
- `03_РЕФЕРЕНСЫ/moodboard.html` — визуальная доска с карточками референсов (генерируется через `render.py`)

## Процесс работы

1. Проверяет `.landing-state.yaml` — stage должен быть `03_references`, иначе STOP
2. Запускает `render-pipeline-map.sh` и показывает Mermaid-карту пользователю
3. Создаёт TodoWrite со всеми оставшимися этапами
4. Проходит `gate-check.sh --stage 03_references` — при exit != 0 останавливается
5. Читает одобренные референсы, уточняет у пользователя теги каждого
6. Пишет `moodboard.md` с описанием визуального направления
7. Запускает `python3 skills/moodboard-creation/scripts/render.py` для генерации HTML
8. **HARD GATE**: ждёт явного одобрения пользователя после просмотра `moodboard.html`

**Важно:** Если референс попадает в red flag из `visual-requirements.md` секции 6 — не сохранять.

## Связанные концепты
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit действием
- [[moodboard-creation]] — скилл, содержащий `render.py` для генерации HTML-доски
- [[landing-orchestrator]] — оркестратор, который вызывает этот агент в нужный момент
- [[landing-references]] — команда сбора референсов (предшествующий этап)
- [[landing-brand]] — следующий этап после утверждения мудборда

## Источник
- `agents/moodboard-composer.md`