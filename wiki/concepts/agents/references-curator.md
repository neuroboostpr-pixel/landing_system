---
type: agent
name: references-curator
sources: ["agents/references-curator.md"]
updated: 2026-05-20
triggers: ["собери референсы", "добавь референс", "этап 03 референсы", "/landing-references"]
stage: "03"
uses: ["moodboard-composer", "stage-execution-protocol", "niche-analyst", "landing-orchestrator"]
tags: ["stage-03", "references", "visual", "index"]
---

# references-curator — сборщик визуальных референсов

## Что делает

Собирает визуальные референсы для будущего дизайна лендинга: принимает ссылки на сайты, Behance, Dribbble и скриншоты, присваивает каждому статус и ведёт структурированный файл `03_РЕФЕРЕНСЫ/index.yaml`. Когда набрано минимум три одобренных референса — передаёт управление агенту [[moodboard-composer]].

## Когда вызывать / в каком этапе

Активируется на **этапе 03** (`03_references`) после завершения анализа ниши (01a). Запускается командой `/landing-references` или оркестратором. Требует, чтобы `.landing-state.yaml` показывал `current_stage == 03_references`; если нет — останавливается и сообщает пользователю.

Перед любым действием агент обязан:
1. Прочитать `.landing-state.yaml` и показать Mermaid-карту через `render-pipeline-map.sh`.
2. Пройти `gate-check.sh --stage 03_references` (exit 0).
3. Создать TodoWrite со всеми оставшимися этапами.

## Что на вход / на выход

**Вход:**
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `visual_notes` конкурентов (что нельзя копировать).
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — Section 6 «red flags»: запрещённые визуальные приёмы.
- Ссылки и скриншоты от пользователя (URL, Behance, Dribbble, перетащенные файлы в `03_РЕФЕРЕНСЫ/refs/`).

**Выход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — список референсов с полями: url / file, status (`candidate` / `approved` / `rejected`), примечания.
- **HARD GATE:** минимум 3 референса со статусом `approved`. Без этого [[moodboard-composer]] не запустится.

## Ключевые ограничения

- Референсы, попадающие под «red flags» из `visual-requirements.md`, **отклоняются автоматически** со ссылкой на конкретный пункт.
- Нельзя клонировать визуал лидеров категории — агент ищет незанятые визуальные «gaps».
- Физический блок на Write/Edit через хук `enforce_stage_gate.py` — не обходить, закрывать предшественника.

## Связанные концепты

- [[moodboard-composer]] — принимает управление после набора 3+ approved-референсов
- [[niche-analyst]] — поставляет `competitors.yaml` и `visual-requirements.md` как обязательный input
- [[stage-execution-protocol]] — протокол запуска любого этапа (чтение state, gate-check, TodoWrite)
- [[landing-orchestrator]] — вызывает агента в нужный момент pipeline

## Источник

- `agents/references-curator.md`