---
type: agent
name: references-curator
sources: ["agents/references-curator.md"]
updated: 2026-05-20
triggers: ["этап 03", "собрать референсы", "добавить ссылки на сайты", "referenceы для дизайна", "подобрать визуальные примеры"]
stage: "03"
uses: ["moodboard-composer", "niche-analyst", "references-collection", "landing-orchestrator", "stage-execution-protocol"]
tags: ["references", "stage-03", "visual", "index"]
---

# References Curator — Сбор Визуальных Референсов

## Что делает
Собирает ссылки на понравившиеся сайты, файлы Behance/Dribbble и скриншоты, присваивает каждому статус (кандидат / одобрен / отклонён) и ведёт реестр `03_РЕФЕРЕНСЫ/index.yaml`. Как только набирается минимум три одобренных референса — передаёт управление агенту `moodboard-composer`.

## Когда вызывать / в каком этапе
Активируется в **первой половине этапа 03** (References). Запускается командой `/landing-references` через `landing-orchestrator`. Обязательное условие: `.landing-state.yaml` проекта должен показывать `current_stage == 03_references`. Если предшествующие этапы (00–02) не закрыты, `enforce_stage_gate.py` заблокирует все записи.

## Что на вход / на выход

**Вход:**
- Ссылки, Behance/Dribbble-файлы и скриншоты от пользователя → папка `03_РЕФЕРЕНСЫ/refs/`
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `visual_notes` каждого конкурента; нужно, чтобы не копировать визуал лидеров рынка
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — Секция 6 (red flags): любой референс, попадающий под запрет, автоматически отклоняется со ссылкой на конкретный пункт

**Выход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — реестр референсов со статусами `candidate / approved / rejected`
- Одобренный набор (≥3 референса) передаётся агенту `moodboard-composer`

## Связанные концепты
- [[moodboard-composer]] — принимает одобренный набор и строит нарратив + HTML-мудборд
- [[niche-analyst]] — производит `competitors.yaml` и `visual-requirements.md`, которые агент читает перед поиском референсов
- [[references-collection]] — скилл с утилитой `index.py` (add / update / list) для работы с реестром
- [[landing-orchestrator]] — управляет stage-gates и вызывает агента в нужный момент
- [[stage-execution-protocol]] — обязательный протокол: читай `.landing-state.yaml`, показывай Mermaid-карту, проверяй `gate-check.sh` перед любым Write/Edit

## Источник
- `agents/references-curator.md`