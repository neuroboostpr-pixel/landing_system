---
type: agent
name: references-curator
sources: ["agents/references-curator.md"]
updated: 2026-05-26
triggers: []
stage: "03"
uses: ["landing-orchestrator", "moodboard-composer", "stage-execution-protocol"]
tags: ["stage-03", "references", "visual", "index"]
---

# References Curator — агент сбора визуальных референсов

## Что делает
Собирает визуальные примеры сайтов от клиента (ссылки, скриншоты, Behance-файлы), присваивает каждому статус и ведёт индекс `03_РЕФЕРЕНСЫ/index.yaml`. Как только накоплены минимум 3 одобренных референса — передаёт управление агенту moodboard-composer.

## Когда вызывать / в каком этапе
Активируется на **этапе 03 (сбор референсов)** pipeline-а. Условие запуска — `.landing-state.yaml` показывает `current_stage == 03_references`. Агент не начинает запись файлов, пока `gate-check.sh` не вернёт exit 0. Предшественник — этап `01a_АНАЛИЗ_НИШИ` с готовыми `competitors.yaml` и `visual-requirements.md`.

## Что на вход / на выход

**Вход:**
- Ссылки на сайты, Behance / Dribbble, скриншоты от пользователя в `03_РЕФЕРЕНСЫ/refs/`
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `visual_notes` конкурентов (обязательно к прочтению перед поиском)
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — секция 6 «red flags» (обязательна: любой референс проверяется против запретов)

**Выход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — индекс всех референсов с полями `status: candidate | approved | rejected`
- HARD GATE: минимум 3 референса со статусом `approved` для передачи управления

## Алгоритм работы
1. Читает `.landing-state.yaml`, убеждается в правильном этапе.
2. Запускает `render-pipeline-map.sh` и показывает Mermaid-карту пользователю.
3. Создаёт TodoWrite-список всех оставшихся этапов.
4. Запускает `gate-check.sh --stage 03_references`.
5. Просит у пользователя референсы; для URL-ов сохраняет ссылку (скриншот — в Phase 5).
6. Для каждого референса уточняет статус у пользователя.
7. Обновляет индекс через `python3 skills/references-collection/scripts/index.py add|update|list`.
8. Проверяет каждый референс против red flags из `visual-requirements.md`; отвергает нарушителей с указанием конкретного пункта.
9. По достижении ≥3 approved — запускает `verify-03_references.sh` и закрывает этап через `gate-state.sh approve`.

## Связанные концепты
- [[landing-orchestrator]] — вызывает агента на этапе 03 и получает управление обратно после approve
- [[moodboard-composer]] — следующий агент в цепочке, принимает одобренный набор референсов
- [[stage-execution-protocol]] — обязательный протокол предусловий перед любой записью файлов

## Источник
- `agents/references-curator.md`