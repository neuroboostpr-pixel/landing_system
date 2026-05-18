---
type: rule
name: pr-j-static-prompts-identity
sources: ["docs/superpowers/specs/2026-05-16-pr-j-static-prompts-identity-design.md"]
updated: 2026-05-16
triggers: []
stage: "07c, 07f"
uses:
  - gpt5-prompting-engine
  - photo-curation
  - paralaximus-codex
  - stage-gates
  - 07c-photos
  - 07f-composed-final
tags: [identity, prompts, codex, photo-pipeline, hardening]
---

# PR-J — Стационарные промпты + Identity Hardening

## Что делает
Усиливает два слабых места системы: (1) все codex-промпты переводятся в стационарные файлы, проверенные через `gpt5-prompting-engine` со скором ≥8/10; (2) проверка идентичности фото при обработке становится умнее — порог допустимых изменений зависит от типа слота, а при нарушении pipeline откатывает на оригинал вместо полного отказа.

## Когда вызывать / в каком этапе
Это спецификация изменений, а не команда. Затрагивает этапы **07c** (soft gate — предупреждение при identity violation) и **07f** (hard gate — нельзя задеплоить с нарушениями). Применяется при реализации PR-J в системе.

## Что на вход / на выход

**Часть A — Стационарные промпты:**
- Вход: `skills/paralaximus-codex/templates/atlas-prompt.md` и `skills/photo-curation/templates/codex-photo-prompt.md` (написаны без engine)
- Выход: те же файлы, но перегнанные через `gpt5-prompting-engine` с валидацией ≥8/10; старые версии → `*.legacy.md`

**Часть B — Identity Hardening:**
- Вход: обработанная фотка + оригинал + тип слота (`portrait`, `vehicle`, `product`, …)
- Выход: при нарушении — оригинал с resize (без codex), в manifest запись `identity_violation: true` + дистанция + порог
- Скрипт `verify-identity-preserved.sh` проверяет manifest перед 07f

**Пороги по типу:**

| Тип слота | Порог (max Hamming distance) |
|---|---|
| portrait / team / expert | 5 (строго) |
| vehicle / car | 10 |
| product | 8 |
| hero-bg / interior | 12–15 |

## Связанные концепты
- [[gpt5-prompting-engine]] — инструмент валидации промптов (score rubric ≥8/10)
- [[photo-curation]] — скилл, чьи `identity-check.py` и `photo-pipeline.py` модифицируются
- [[paralaximus-codex]] — скилл с `atlas-prompt.md`, требующим миграции через engine
- [[stage-gates]] — добавляются soft check на 07c и hard check на 07f
- [[07c-photos]] — этап, где применяются новые пороги (soft warning)
- [[visual-qa]] — параллельная защита идентичности через визуальную проверку (PR-I.b)

## Источник
- `docs/superpowers/specs/2026-05-16-pr-j-static-prompts-identity-design.md`