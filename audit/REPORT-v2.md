# Audit Report v2 — Landing-System (Master)

**Дата:** 2026-05-20
**Контекст:** Повторный аудит после 40 коммитов Top-10 фиксов (tag `audit-fixes-2026-05-20`)
**Методология:** code-reviewer (Jeffallan/claude-skills) — 5 параллельных subagent-ов
**Зоны:** 1) Python, 2) Bash, 3) Agents/Skills/Commands, 4) Enforcement layer, 5) **NEW: End-to-end functional risks**

**Verdict v2:** ✅ **Top-10 фиксы подтверждены работающими**, но система **НЕ готова к массовому тесту** — 5 высокоприоритетных gap'ов (3 NEW + 2 deferred) могут заблокировать прод-сценарий.

---

## ✅ Что Top-10 закрыл (подтверждено независимыми reviewer'ами)

| # | Фикс | Где подтверждено | Свидетельство |
|---|---|---|---|
| 1 | PreToolUse hook реально блокирует | Zone 4 | Сценарий end-to-end проверен: попытка Write в `04_БРЕНД/` пока `03_references: locked` → exit 2 |
| 2 | Stage Execution Protocol на 22 stage-агентах + 10 helper-маркерах | Zone 3 | 33/33 покрытие, нет leftover `<STAGE>` |
| 3 | gate-check unknown types hard-fail + 2 новых типа | Zone 2 | `dir_has_files` дополнительно отвергает brace-patterns |
| 4 | legacy bypass strict (allowlist + reason + log) | Zone 2 + 4 | `legacy_allowed: []` default-deny |
| 5 | O(N²) cache в system_compiler | Zone 1 | `save_cache` вне цикла, `(compiled or errors)` guard |
| 6 | SDK error hash cache | Zone 1 | hash сохраняется перед `continue` в SDKError ветке |
| 7 | post-commit hook safety | Zone 2 | merge/rebase guards, `--no-verify` удалён, explicit paths |
| 8 | Template `n/a → locked` defaults | Zone 4 | Подтверждено в template |
| 9 | 4 broken file refs | Zone 3 | ACF/brief/prototype/quiz — все 4 фикснуты |
| 10 | PR-D contradictions | Zone 3 | Orchestrator Phase 1 Scope удалён, 5 commands очищены |

**Регрессий — 0.** Все тесты проходят (78/78 pytest, 19/21 bats — 2 pre-existing).

**Бонус-фиксы (не были в плане Top-10):**
- `verify-visual-qa.sh` подключён в `landing-final-check.sh` (был orphan)
- macOS `seq 0 -1` workaround в gate-check.sh
- GATES_YAML env override (testability)

---

## 🔴 NEW findings (введены или обнаружены при re-audit)

### N1 — `PIPELINE_ORDER` ≠ `stage-gates.yaml` (HIGH) — найдено Zone 1 + Zone 4

**Где:** `scripts/hooks/enforce_stage_gate.py:40`

**Проблема:** в Python-константе `PIPELINE_ORDER` стадии идут:
```
... 08_build, 09_deploy, 10_qa, 11_analytics, 12_seo
```

А в `config/stage-gates.yaml:391`:
```
09_deploy require_approved: ["08_build", "10_qa"]
```

**Следствия:**
1. Hook **разрешит Write в 09_деплой** когда `10_qa` ещё `locked` (chicken-and-egg)
2. Hook **заблокирует Write в 10_QA** пока `09_deploy` не `approved` (impossible)
3. `gate-check.sh` (читает YAML) и hook (читает Python) дадут **разные вердикты** на одинаковом state

**Severity:** HIGH — двойной enforcement рассинхронизирован. Чинится 1-строчной перестановкой + dedup constant.

**Fix:** убрать дублирование. Либо hook читает `_stage_paths.yaml` + строит порядок из `stage-gates.yaml`, либо PIPELINE_ORDER переставить и добавить тест на synchronization.

### N2 — `.claude/commands/` runtime копии desynced (HIGH) — найдено Zone 3

**Где:**
- `.claude/commands/landing-content.md` — ВСЁ ЕЩЁ имеет `07_КОНТЕНТ/prototype.md` (Phase 7 фиксил только `commands/landing-content.md`)
- `.claude/commands/landing-go.md` — пропустил 17-строчный блок n/a transition из Phase 3.2
- `.claude/commands/landing-qa.md` — это **два разных** command'а под одним slug

**Severity:** HIGH — Claude Code исполняет `.claude/commands/`, не `commands/`. Source-of-truth divergence = пользователь получает старую логику.

**Fix:** автоматическая синхронизация `commands/ → .claude/commands/` (symlink или CI-проверка). Phase 9 сделал ручной sync — не масштабируется.

### N3 — `Bash` tool не в PreToolUse matcher (MEDIUM) — найдено Zone 4

**Где:** `.claude/settings.json` — matcher `Write|Edit|MultiEdit`

**Проблема:** агент может обойти hook через `Bash(cat > 05_ДИЗАЙН/file.md)`, `bash -c 'echo ... >>'`, перенаправления.

**Severity:** MEDIUM — целенаправленный обход возможен. Для добросовестного агента это не проблема, но enforcement не должен полагаться на добросовестность.

**Fix:** расширить matcher до `Write|Edit|MultiEdit|Bash` + добавить в `enforce_stage_gate.py` парсинг bash-команд (детектировать `>`, `>>`, `tee`, `cp` с целевым путём в pipeline).

### N4 — `codex` CLI hidden dependency без gate-check (HIGH) — найдено Zone 5

**Где:** `/landing-photos` (07d) + `/landing-visuals` (07e) — оба требуют `codex` + `codex login`. **Нет ни одного gate-check'а**, который бы проверил.

**Проблема:** ~50% пайплайна (визуальный контент) зависит от codex. `scripts/install-codex.sh` существует, но не вызывается. Маркетолог запустит `/landing-photos` без codex → агент упадёт mid-stage с cryptic ошибкой.

**Severity:** HIGH для mass-testing scenario.

**Fix:** добавить hard_check `cli_available: codex` в `stage-gates.yaml` для 07d и 07e. Реализовать тип `cli_available` в gate-check.sh.

### N5 — Onboarding optional in practice (HIGH) — найдено Zone 5

**Где:** `~/.landing-system/setup_complete` flag проверяется **только** в `scripts/deploy.sh` (этап 09).

**Проблема:** `/landing-go`, `/landing-photos`, `/landing-build` НЕ проверяют. Новый оператор может пройти 8 этапов и обнаружить пустой `.env` только перед деплоем (часы потеряны).

**Severity:** HIGH для onboarding-сценария.

**Fix:** добавить setup_complete check в начале `/landing-go` и в первом этапе любой команды.

---

## 🟡 REMAINS (Top-10 их явно отложил — статус)

Все 10 deferred Python items REMAIN (Cluster C, F):
- `lint.py:121` — 235K без кэша
- `sdk_client.py:53` — `max_turns=50` (должен быть 1) — **token bleed**
- `flush.py:88` — swallowed SDK errors
- `hash_cache.py:19` — corrupt cache silent → mass re-compile
- `hash_cache.py` — non-atomic write (docstring врёт «атомарно»)
- `cleanup_broken_links.py:42` — non-atomic
- `verify_photo_pipeline.py._find_block_meta` — per-img walk
- `session_end.py`/`pre_compact.py` — trust stdin transcript_path
- `system_compiler.py` — repo walked twice
- `lint.py` — files read twice

Cluster D + E (bash):
- `eval` в `landing-final-check.sh:33` — code injection vector
- `verify-composed-premium.sh` parallax regex too wide
- `verify-composed-has-visuals.sh` placeholder regex too narrow (`[ICON:`, `[CHART:`, `[VISUAL:`, `[PHOTO:`, `[ФОТО:`, `[ИКОНКА:` не ловятся)
- `verify-*.sh` mostly без `set -e`
- `check-deps.sh` не валидирует `yq`/`pyyaml`/`python3`/`php`/`curl`

Cluster B (prompts) — R1, R2, R3, R5:
- **R1:** 4 stale ACF refs survived Phase 7: `landing-orchestrator.md:167`, `wp-deployer.md:34`, `commands/landing-deploy.md:24,37`, `skills/landing-versioning-and-cloning/scripts/create-version.sh:14`
- **R2:** Phase 2/3/4/5 obsolete Scope blocks в orchestrator (lines 74/106/134/157) — Phase 8 удалил только Phase 1
- **R3:** orchestrator preamble (4-step) drift от canonical `stage-agent-preamble.md` (7-step)
- **R5:** `frontend-builder` zero-JS escape hatch unchanged

Cluster A (enforcement gaps):
- **M6:** soft-check non-yes/no still treated as pass
- **C3:** `gate-check.sh:247-263` script verifier ran TWICE on failure (double tokens + flaky) — это originally CRITICAL-3, **НЕ закрыто Top-10**
- **C4:** `verify-composed-premium.sh` только на 07c/07f (08/09 не перепроверяют)
- **D1:** Anthropic SDK auth не в `validate-all.sh`
- **D2:** `verify-php-syntax.sh` exit 2 без hint
- **D3:** Нет pre-deploy проверки WP installed на Beget

---

## ⚪ Pre-existing (не в v1, нашлось при re-audit)

- `hash_cache.save_cache` docstring врёт «атомарно» (zone 1)
- 4 stale ACF references в файлах вне Phase 7 scope (zone 3, R1)
- 3 stale «вызывается ВРУЧНУЮ» notes в `CLAUDE.md` (lines 30/47/69) (zone 4)
- `01_context` в hook PIPELINE_ORDER без объявления в `stage-gates.yaml` (zone 4)
- Phase 2 minor: post-commit `git add` не включает `wiki/.cache.json` → check-wiki-sync drift (zone 2 N6)

---

## 🎯 Приоритизированный fix-list (батч до массового теста)

**Минимально перед mass test (HIGH severity, всего ~3 часа):**

| Prio | Fix | Severity | Время | Source |
|---|---|---|---|---|
| 1 | **N1** — PIPELINE_ORDER ↔ stage-gates.yaml sync | HIGH | 30 мин | Zone 1+4 |
| 2 | **N2** — `.claude/commands/` auto-sync mechanism | HIGH | 1 час | Zone 3 |
| 3 | **N4** — `cli_available: codex` gate для 07d/07e | HIGH | 30 мин | Zone 5 |
| 4 | **N5** — `setup_complete` check в начале `/landing-go` | HIGH | 20 мин | Zone 5 |
| 5 | **C3** — gate-check script-double-execution (originally CRITICAL) | HIGH | 30 мин | Zone 4 |
| 6 | **R1** — 4 stale ACF refs (Phase 7 follow-up) | MEDIUM | 30 мин | Zone 3 |

**Опционально перед mass test (MEDIUM, ещё ~2 часа):**

| Prio | Fix | Severity | Время |
|---|---|---|---|
| 7 | **N3** — Bash tool в PreToolUse matcher (closes shell-escape) | MEDIUM | 1 час |
| 8 | **R2** — оставшиеся obsolete Scope блоки в orchestrator | MEDIUM | 15 мин |
| 9 | **D1** — Anthropic SDK auth в validate-all.sh | MEDIUM | 20 мин |
| 10 | **D6** — `sdk_client.py:53` max_turns=50 → 1 (token bleed) | MEDIUM | 5 мин |
| 11 | Cluster F correctness (hash_cache, flush.py) | MEDIUM | 1 час |

**После mass test (low priority cosmetic / perf):**

- Cluster C/E полностью (lint.py, regex'ы, set -e в verify-*)
- D8 — `eval` в landing-final-check.sh
- Phase 2 minor cleanups (--absolute-git-dir, better trap, wiki/.cache.json в add list)
- R3, R5 — preamble drift, frontend-builder escape hatch

---

## Источники

- 📄 [audit/v2-01-scripts-wiki-python.md](v2-01-scripts-wiki-python.md)
- 📄 [audit/v2-02-scripts-bash.md](v2-02-scripts-bash.md)
- 📄 [audit/v2-03-agents-skills-commands.md](v2-03-agents-skills-commands.md)
- 📄 [audit/v2-04-enforcement-layer.md](v2-04-enforcement-layer.md)
- 📄 [audit/v2-05-functional-risks.md](v2-05-functional-risks.md)

---

## Bottom Line

### Готова ли система для solo-режима (1 лендинг)?
**Да, осторожно.** Top-10 фиксы работают. Главные ловушки — codex без проверки + onboarding optional + `.claude/commands/` desync.

### Готова ли для массового теста (10+ лендингов, новые операторы)?
**Нет.** 5 HIGH-severity gap'ов (N1, N2, N4, N5, C3) могут заблокировать прод-сценарий. Batch ~3-4 часа закрывает базовый риск.

### Главный enforcement primitive работает?
**Да.** PreToolUse hook реально блокирует — это центральное доказательство Phase 5. Но **N1 (PIPELINE_ORDER mismatch)** означает что в edge-cases он даёт chicken-and-egg.
