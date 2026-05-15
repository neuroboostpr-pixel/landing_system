---
type: agent
name: references-curator
sources: ["agents/references-curator.md"]
updated: 2026-05-15
triggers: []
stage: "03"
uses: ["moodboard-composer", "niche-analyst", "references-collection"]
tags: ["references", "stage-03", "visual", "index"]
---

# references-curator — сборщик визуальных референсов

## Что делает
Собирает визуальные референсы (URL-сайтов, Behance/Dribbble, скриншоты), присваивает каждому статус и ведёт реестр в `03_РЕФЕРЕНСЫ/index.yaml`. Работает в первой половине этапа 03 — до передачи управления в `moodboard-composer`.

## Когда вызывать / в каком этапе
Этап **03** (сбор референсов). Запускается после того, как завершён анализ ниши (этап 01a) и у проекта есть `competitors.yaml` с визуальными заметками конкурентов. Агент активен до тех пор, пока не наберётся минимум 3 референса со статусом `approved`.

## Что на вход / на выход

**Вход:**
- URL-ссылки, файлы с Behance/Dribbble, скриншоты, перетащенные в `03_РЕФЕРЕНСЫ/refs/`
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — поле `visual_notes` каждого конкурента обязательно к прочтению перед поиском
- `01a_АНАЛИЗ_НИШИ/visual-requirements.md` — раздел 6 (red flags) проверяется при оценке каждого референса

**Выход:**
- `03_РЕФЕРЕНСЫ/index.yaml` — реестр всех референсов со статусами `candidate` / `approved` / `rejected`
- Передача управления агенту `moodboard-composer` после прохождения HARD GATE

## HARD GATE
Агент **не передаёт управление** `moodboard-composer`, пока количество референсов со статусом `approved` не достигнет **минимум 3**. Референсы, попадающие в запреты из `visual-requirements.md`, отвергаются автоматически со ссылкой на конкретный пункт.

## Процесс работы
1. Запрашивает у пользователя референсы (URL / файлы / скриншоты).
2. Для каждого URL по возможности захватывает скриншот (Phase 2 — хранит только URL).
3. Предлагает пользователю присвоить статус: `candidate`, `approved` или `rejected`.
4. Управляет `index.yaml` через скрипт `python3 skills/references-collection/scripts/index.py add|update|list`.
5. Перед оценкой нового референса сверяется с `visual_notes` конкурентов — не клонировать визуал лидеров категории, искать визуальные gaps.

## Связанные концепты
- [[moodboard-composer]] — принимает управление после HARD GATE; строит мудборд из approved-референсов
- [[niche-analyst]] — поставляет `competitors.yaml` и `visual-requirements.md`, которые агент обязан прочитать перед работой
- [[references-collection]] — скилл, содержащий скрипт `index.py` для управления реестром

## Источник
- `agents/references-curator.md`