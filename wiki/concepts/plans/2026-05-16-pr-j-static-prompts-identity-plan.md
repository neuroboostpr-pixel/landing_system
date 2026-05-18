---
type: unknown
name: pr-j-static-prompts-identity-plan
sources: ["docs/superpowers/plans/2026-05-16-pr-j-static-prompts-identity-plan.md"]
updated: 2026-05-18
triggers: []
stage: "07c, 07f"
uses:
  - gpt5-prompting-engine
  - paralaximus-codex
  - photo-curation
  - stage-gates
  - visual-generation
tags: ["plan", "identity", "photo", "prompts", "pr-j"]
---

# PR-J — Static Prompts + Identity Hardening (план реализации)

## Что делает
Улучшает два AI-промпта через движок GPT-5 и добавляет жёсткую защиту клиентских фотографий от нежелательных изменений: система не может «переделать» машину в другую модель или «улучшить» лицо человека на снимке — любое нарушение автоматически откатывается к оригиналу.

## Когда вызывать / в каком этапе
Реализуется однократно как PR-J. Затрагивает этапы 07c (обработка фото, soft warning) и 07f (финальная композиция, жёсткий GATE). После завершения помечает Пункт 4 в `docs/ПЛАН-ДОРАБОТОК.md` как выполненный.

## Что на вход / на выход

**Вход:**
- `skills/paralaximus-codex/templates/atlas-prompt.md` — текущий промпт генерации атласа
- `skills/photo-curation/templates/codex-photo-prompt.md` — текущий промпт обработки фото
- `skills/photo-curation/scripts/identity-check.py` — скрипт проверки идентичности
- `skills/photo-curation/scripts/photo-pipeline.py` — пайплайн обработки фото
- `config/stage-gates.yaml` — конфигурация гейтов

**Выход:**
- `atlas-prompt.md` v2 (через engine, score ≥8/10) + `.legacy.md` бекап
- `codex-photo-prompt.md` v2 с identity-strict правилами + `.legacy.md` бекап
- `identity-check.py` с per-type порогами: portrait/team=5, vehicle=10, product=8, hero-bg=12, interior=15, background=18
- `photo-pipeline.py` с revert-логикой: при нарушении identity → откат на оригинал, запись `identity_violation: true` в manifest
- `scripts/verify-identity-preserved.sh` — проверяет manifest на наличие нарушений
- `config/stage-gates.yaml` — soft check на 07c, hard check на 07f
- `tests/pr-j/` — 8 bats-тестов (thresholds, verify, revert manifest)

## Связанные концепты
- [[gpt5-prompting-engine]] — используется для валидации и улучшения atlas-prompt и codex-photo-prompt (classify=migrate/create, score ≥8/10)
- [[paralaximus-codex]] — владеет atlas-prompt.md, генерирует 2K параллакс-атласы через codex image_gen
- [[photo-curation]] — владеет codex-photo-prompt.md, identity-check.py, photo-pipeline.py
- [[stage-gates]] — конфиг, куда добавляются soft (07c) и hard (07f) проверки identity
- [[visual-generation]] — смежный скилл генерации визуала, использует аналогичный codex подход
- [[07c-photos]] — этап обработки фото, получает soft warning при identity violation
- [[07b-composed]] — финальная composed.html блокируется на 07f если есть violations

## Источник
- `docs/superpowers/plans/2026-05-16-pr-j-static-prompts-identity-plan.md`