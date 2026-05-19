---
type: script
name: render-pipeline-map
language: bash
sources: ["scripts/render-pipeline-map.sh"]
updated: 2026-05-19
---

# render-pipeline-map.sh

Рендерит Mermaid-карту pipeline проекта-лендинга из его `.landing-state.yaml`.
Используется `landing-orchestrator` в Шаге 1 обязательного протокола
([`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md)).

## Что делает

1. Читает статусы всех этапов pipeline из `.landing-state.yaml`
2. Рисует Mermaid flowchart с цветами по статусам:
   - ✓ Зелёный — `approved`
   - ▶ Оранжевый — `in_progress`
   - ✗ Красный — `failed`
   - ○ Серый — `locked`
   - — Пунктир — `n/a`
3. Печатает сводку (счётчики статусов)
4. Указывает следующий шаг

## Usage

```bash
# Только в stdout (для показа в чате)
bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml

# В stdout И в wiki проекта одновременно
bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
```

С флагом `--write-wiki` карта дополнительно сохраняется в
`<project>/wiki/pipeline-map.md` (auto-generated, не редактировать руками).

## Когда вызывается

- Шаг 1 Stage Execution Protocol — orchestrator в начале каждого прогона
- Hook после `gate-check.sh --approve` (опционально, для обновления вики)
- Любая ad-hoc проверка «где сейчас проект»

## Зависимости

- `yq` (mikefarah/yq) — `brew install yq`

## Источник

- `scripts/render-pipeline-map.sh`
