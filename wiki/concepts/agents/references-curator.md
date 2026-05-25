---
type: agent
name: references-curator
sources: ["agents/references-curator.md"]
updated: 2026-05-25
triggers: []
stage: "03"
uses: ["landing-orchestrator", "moodboard-composer", "niche-analyst"]
tags: ["stage-03", "references", "visual", "curator"]
---

# References Curator — Агент сбора визуальных референсов

## Что делает

Собирает визуальные референсы для лендинга (ссылки на сайты, Behance, скриншоты), присваивает каждому статус (candidate / approved / rejected) и ведёт файл `03_РЕФЕРЕНСЫ/index.yaml`. Когда набирается минимум 3 одобренных референса — передаёт управление агенту moodboard-composer.

## Когда вызывать / в каком этапе

Запускается в **этапе 03 (03_references)** pipeline. Активируется автоматически через `landing-orchestrator` или вручную. Перед стартом проверяет `.landing-state.yaml` — должен быть `current_stage == 03_references`, иначе останавливается и сообщает об ошибке.

## Что на вход / на выход

**Входящие артефакты:**
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — визуальные заметки по конкурентам (поле `visual_notes`); агент читает их, чтобы не клонировать визуал лидеров
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — раздел 6 (red flags); каждый референс проверяется на запрещённые паттерны

**Исходящие артефакты:**
- `03_РЕФЕРЕНСЫ/index.yaml` — индекс всех референсов с указанием URL, пути к файлу и статуса
- `03_РЕФЕРЕНСЫ/refs/` — папка со скриншотами и файлами

**Жёсткий гейт (HARD GATE):** минимум 3 референса со статусом `approved` — только тогда этап закрывается.

## Процесс

1. Просит пользователя предоставить референсы: URL, файлы Behance/Dribbble, перетаскиваемые скриншоты в `03_РЕФЕРЕНСЫ/refs/`
2. Для каждого URL пытается сохранить скриншот (в текущей фазе — только URL, без headless-браузера)
3. Спрашивает пользователя статус каждого референса: candidate / approved / rejected
4. Управляет `index.yaml` через `python3 skills/references-collection/scripts/index.py add|update|list`
5. Проверяет каждый референс по red-flags из `visual-requirements.md`; нарушающие запреты — отклоняет со ссылкой на конкретный пункт
6. По достижении 3 approved — закрывает этап через `gate-state.sh approve`

## Связанные концепты

- [[landing-orchestrator]] — вызывает этого агента в рамках общего pipeline
- [[moodboard-composer]] — принимает управление после закрытия этапа 03
- [[niche-analyst]] — поставляет `competitors.yaml` и `visual-requirements.md`, которые агент обязан прочесть перед работой

## Источник

- `agents/references-curator.md`