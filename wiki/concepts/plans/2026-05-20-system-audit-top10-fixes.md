---
type: rule
name: 2026-05-20-system-audit-top10-fixes
sources: ["docs/superpowers/plans/2026-05-20-system-audit-top10-fixes.md"]
updated: 2026-05-20
triggers: []
stage: ""
uses:
  - gate-check
  - landing-orchestrator
  - enforce-stage-gate
  - system-compiler
  - landing-state
  - stage-gates
  - post-commit
tags: [audit, enforcement, token-leaks, plan, fixes, gates]
---

# Top-10 Audit Fixes — план реализации (2026-05-20)

## Что делает

Закрывает 10 критичных находок аудита `audit/REPORT.md` — превращает систему из «политики без полиции» в механизм, где пропуск pipeline-шага физически невозможен, а вспомогательные скрипты не тратят токены впустую на каждом `git commit`.

## Когда вызывать / в каком этапе

Применяется один раз — при исполнении технического спринта после получения `audit/REPORT.md`. Исполнителю рекомендован skill `superpowers:subagent-driven-development`. Каждый task атомарен: failing test → fix → green test → commit.

## Что на вход / на выход

**Вход:**
- `audit/REPORT.md` — 10 кластеров с точными строчными ссылками
- Исходники: `scripts/wiki/system_compiler.py`, `scripts/gate-check.sh`, `.githooks/post-commit`, `template/.landing-state.yaml`, `agents/*.md`, `commands/*.md`, `.claude/settings.json`

**Выход (8 фаз):**

| Фаза | Находки | Ключевые артефакты |
|------|---------|-------------------|
| 1 | #5, #6 — токен-утечки wiki | `system_compiler.py` — кэш O(N²) → O(N), hash при SDK-ошибке |
| 2 | #7 — post-commit рекурсия | `.githooks/post-commit` — guards для merge/rebase, убрать `--no-verify` |
| 3 | #8 — шаблон defaults `n/a` | `template/.landing-state.yaml` — `locked` вместо `n/a` для upstream стадий |
| 4 | #3, #4 — gate-check дыры | `gate-check.sh` — hard-fail на unknown types, реализация `file_or_dir_exists` / `dir_has_files`, allowlist для legacy-bypass |
| 5 | **#1 — главное** | `scripts/hooks/enforce_stage_gate.py` + wiring в `.claude/settings.json` — физический PreToolUse-блок |
| 6 | #2 — Stage Execution Protocol | 28 агентов — вставка preamble из `docs/standards/stage-agent-preamble.md` |
| 7 | #9 — битые пути | `integrations-engineer`, `seo-optimizer`, `content-writer`, `prototype-importer` |
| 8 | #10 — PR-D противоречия | 5 command-файлов + `landing-orchestrator.md` — убрать «не интегрировано» |

Финал: `bats tests/gate-check/*.bats && pytest tests/gate-check/ tests/wiki/ -v` → все PASS, тег `audit-fixes-2026-05-20`.

## Связанные концепты

- [[gate-check]] — скрипт, который расширяется в Phase 4 (новые типы проверок + строгий legacy)
- [[landing-orchestrator]] — агент, в котором удаляется устаревший «Phase 1 Scope» (Phase 8)
- [[system-compiler]] — wiki-компилятор, чинится в Phase 1 (O(N²) IO и hash-cache при ошибке)
- [[post-commit]] — хук, усиливается в Phase 2 (защита от merge-state авто-коммитов)
- [[enforce-stage-gate]] — новый PreToolUse hook, создаётся в Phase 5 (главная находка)
- [[stage-agent-preamble]] — canonical preambula, тиражируется на 28 агентов в Phase 6
- [[landing-state]] — state-файл, дефолты переключаются в Phase 3

## Источник

- `docs/superpowers/plans/2026-05-20-system-audit-top10-fixes.md`