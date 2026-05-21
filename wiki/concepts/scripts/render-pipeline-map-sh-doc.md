---
type: script
name: render-pipeline-map
language: bash
sources: ["scripts/render-pipeline-map.sh", "scripts/render-pipeline-map.sh.doc.md"]
updated: 2026-05-19
triggers:
  - "покажи карту pipeline"
  - "где сейчас проект"
  - "статус этапов"
stage: ""
uses:
  - landing-orchestrator
  - stage-execution-protocol
  - gate-check
tags: ["bash", "pipeline", "mermaid", "visualization", "state"]
---

# render-pipeline-map — визуальная карта прогресса лендинга

## Что делает

Читает файл `.landing-state.yaml` проекта и рисует цветную Mermaid-диаграмму всех этапов pipeline: какие завершены, какой сейчас в работе, какие ещё заблокированы или провалены. Дополнительно печатает сводку по счётчикам статусов и подсказывает, какой шаг следующий.

## Когда вызывать / в каком этапе

Скрипт обязательно запускается в **Шаге 1** протокола `stage-execution-protocol` — то есть перед любым действием на любом этапе. `landing-orchestrator` вызывает его автоматически при каждом прогоне. Также можно запустить вручную для быстрой проверки «где сейчас проект».

Дополнительно вызывается как хук после `gate-check.sh --approve` — чтобы обновить карту в вики проекта.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` конкретного проекта (путь передаётся аргументом)
- Опциональный флаг `--write-wiki`

**Выход:**
- `stdout` — Mermaid flowchart с цветовой кодировкой статусов:
  - ✓ Зелёный — `approved`
  - ▶ Оранжевый — `in_progress`
  - ✗ Красный — `failed`
  - ○ Серый — `locked`
  - Пунктир — `n/a`
- Сводка по счётчикам статусов и подсказка «следующий шаг»
- При флаге `--write-wiki` — файл `<project>/wiki/pipeline-map.md` (авто-генерируемый, редактировать нельзя)

**Пример вызова:**
```bash
# Только вывод в чат
bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml

# Вывод + запись в wiki проекта
bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
```

**Зависимости:** `yq` (mikefarah/yq) — `brew install yq`.

## Связанные концепты

- [[landing-orchestrator]] — вызывает скрипт в Шаге 1 каждого прогона как обязательный протокол
- [[stage-execution-protocol]] — правило, предписывающее показывать Mermaid-карту перед любым действием на этапе
- [[gate-check]] — после проверки гейта может триггерить `--write-wiki` для обновления карты

## Источник

- `scripts/render-pipeline-map.sh`
- `scripts/render-pipeline-map.sh.doc.md`