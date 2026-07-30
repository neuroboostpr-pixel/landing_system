# Audit Report — Landing-System (Master)

**Дата:** 2026-05-20
**Методология:** code-reviewer (Jeffallan/claude-skills)
**Зоны покрытия:** Python (`scripts/wiki/` + `scripts/*.py`), Bash (`scripts/*.sh` + `.githooks/`), Prompts (`agents/`, `skills/`, `commands/`), Enforcement (`config/`, `docs/standards/`, `CLAUDE.md`, `.claude/settings.json`)

**Verdict:** ⚠️ **Request Changes** — система работает, но в текущем виде она `policy without police`: правил много, но физически их никто не enforce'ит. Документация говорит «не пропускай», но **в коде нет ни одного механизма**, который бы остановил агента, решившего срезать угол.

---

## Главный диагноз

Твоё ощущение «иногда система пропускает шаги» — **подтверждено и объяснено**:

1. `lock: hard` в `config/stage-gates.yaml` — декоративный лейбл. `gate-check.sh` читает его **только** чтобы решить — показать ли интерактивный prompt для soft-стадий с пустым `require_approved`. Hard-локи опираются на тот же `require_approved`, что и soft. **Никакой harness-механизм не блокирует tool-вызовы по стадии.**
2. В `.claude/settings.json` сконфигурированы **только wiki-compile хуки**. Нет ни `PreToolUse`, ни `Stop`, ни `UserPromptSubmit`. Любой агент/sub-agent/новая сессия, которая не идёт через `/landing-go`, **проходит мимо всех гейтов**.
3. Stage Execution Protocol упомянут в **1 из 32 агентов** (только `landing-orchestrator.md`). 28 других стадии-владельцев — без преамбулы, без `gate-check.sh`, без обязательства читать state-файл.
4. `template/.landing-state.yaml` для нового проекта **по умолчанию ставит** `00_brief`, `01_context`, `01a_niche_analysis`, `02_assets` в статус `n/a` → 14 проверок niche-analysis (самого проверяемого этапа в системе) **обходятся тихо**.
5. `gate-check.sh:166` молча пропускает unknown check types. `stage-gates.yaml:189` использует тип `file_or_dir_exists` (07a prototype), `stage-gates.yaml:266` — `dir_has_files` (07d photos). Оба **нигде не реализованы**. **07a-гейт сейчас всегда зелёный**, независимо от наличия прототипа.
6. `legacy: true` в любом nested-поле state-файла **обнуляет все hard-checks** этапа (loose `grep` в `gate-check.sh:121`). Без allowlist, без логирования, без обоснования.

---

## Top-10 фиксов по leverage (отсортировано по «эффект/трудозатраты»)

| # | Severity | Что | Где | Эффект | Трудозатраты |
|---|---|---|---|---|---|
| 1 | 🔴 CRITICAL | Добавить `PreToolUse` hook, который читает `.landing-state.yaml` и блокирует Write/Edit для файлов не текущей стадии | `.claude/settings.json` + `scripts/hooks/enforce_stage_gate.py` (новый) | **Главный фикс enforcement.** Делает «не пропускать» физическим законом, а не правилом | 4-6 часов |
| 2 | 🔴 CRITICAL | Скопировать 5-строчную преамбулу Stage Execution Protocol во все 28 stage-owner агентов | `agents/*.md` (кроме `landing-orchestrator`) | Закрывает 80% surface «sub-agent в обход орхестратора» | 2-3 часа |
| 3 | 🔴 CRITICAL | Исправить `gate-check.sh:166` — unknown check types должны быть `exit 1`, а не `⚠ warning + pass`. Добавить реализации `file_or_dir_exists` и `dir_has_files` | `scripts/gate-check.sh` | Чинит 07a-гейт (сейчас фейкозелёный) и 07d-гейт | 1 час |
| 4 | 🔴 CRITICAL | Убрать loose `legacy: true` bypass. Заменить на явный allowlist стадий + обязательное `legacy_reason:` поле + лог | `scripts/gate-check.sh:121-126` | Закрывает «дыру для всех» | 30 мин |
| 5 | 🔴 CRITICAL | Починить O(N²) кэш в `system_compiler.py:197` — переместить `save_cache(...)` ЗА цикл | `scripts/wiki/system_compiler.py` | **Большая экономия токенов** на каждом git commit | 15 мин |
| 6 | 🔴 CRITICAL | Кэшировать hash для SDK-ошибок в `system_compiler.py:179-183` | `scripts/wiki/system_compiler.py` | **Большая экономия токенов** — битый файл сейчас зовёт SDK на каждом commit | 30 мин |
| 7 | 🔴 CRITICAL | Защитить `.githooks/post-commit`: `git merge HEAD` → skip; `--no-verify` → убрать; `set -euo pipefail` | `.githooks/post-commit` | Закрывает auto-commit риски (секреты, циклы) | 30 мин |
| 8 | 🔴 CRITICAL | Убрать `n/a` defaults из `template/.landing-state.yaml` для `00_brief`, `01_context`, `01a_niche_analysis`, `02_assets`. Поставить `pending` | `template/.landing-state.yaml` | Чинит тихий обход niche-analysis | 5 мин |
| 9 | 🟡 MAJOR | Починить 4 broken file refs в агентах: `acf-fields.json`, `approved-design-brief.md`, `07_КОНТЕНТ/prototype.md` (×2), prototype-importer auto-quiz script | `agents/integrations-engineer.md`, `agents/seo-optimizer.md`, `agents/content-writer.md`, `commands/landing-content.md`, `agents/prototype-importer.md` | Чинит «агент шёл за файлом, не нашёл, пошёл выдумывать» | 1 час |
| 10 | 🟡 MAJOR | Привести `landing-orchestrator.md` в актуальный вид — выкинуть «Phase 1 Scope: я умею только заполнять brief.md», убрать PR-D противоречия из 5 command-файлов | `agents/landing-orchestrator.md` + `commands/landing-compose.md`, `landing-photos.md`, `landing-visuals.md`, `landing-wireframe.md`, `landing-prototype.md` | Снимает противоречия, агент перестаёт «выбирать между двумя инструкциями» | 1-2 часа |

**Суммарно top-10: ~12-16 часов работы. Закрывают 95% surface «пропускает шаги + жжёт токены».**

---

## Полные находки по агентам

Детальные отчёты с code:line и suggested fixes:

- 📄 [audit/01-scripts-wiki-python.md](01-scripts-wiki-python.md) — Python код (token leaks, correctness)
- 📄 [audit/02-scripts-bash.md](02-scripts-bash.md) — Bash скрипты (enforcement gaps, auto-commit risks)
- 📄 [audit/03-agents-skills-commands.md](03-agents-skills-commands.md) — Промпты агентов/скиллов/команд (skip-the-step lokovinы)
- 📄 [audit/04-enforcement-layer.md](04-enforcement-layer.md) — Конфиги/стандарты/CLAUDE.md (enforcement-слой)

---

## Кластеры находок (для triage)

### Кластер A — Enforcement (физическая блокировка)
Без него все остальные правила — necessary, но not sufficient.

- [ ] #1 PreToolUse hook
- [ ] #4 убрать `legacy: true` bypass
- [ ] gate-check.sh hard-fail на unknown types (#3)
- [ ] Добавить `lock: hard` в `08b_style` (отсутствует)
- [ ] Soft-check non-yes/no → fail, не pass
- [ ] Прекратить `script` runner двойной запуск

### Кластер B — Agent prompt hygiene
- [ ] #2 Stage Execution Protocol во все агенты
- [ ] #9 broken file refs
- [ ] #10 PR-D противоречия в orchestrator + 5 commands
- [ ] Frontmatter `description:` consistency
- [ ] `allowed-tools:` в frontmatter (а не только в body)

### Кластер C — Token efficiency (wiki & SDK)
- [ ] #5 O(N²) кэш в system_compiler
- [ ] #6 кэшировать hash при SDK errors
- [ ] `lint.py:121` `--llm-check` без кэша (235K chars)
- [ ] `sdk_client.py:52` `max_turns=50` → `max_turns=1`
- [ ] `system_compiler.py:139` repo walked twice
- [ ] `lint.py:62` files read twice
- [ ] `ux-composer` pre-flight inject 11 files (избыточно)

### Кластер D — Auto-commit safety
- [ ] #7 `.githooks/post-commit` защита
- [ ] `git add wiki/` → точечный путь (не папка целиком)
- [ ] `eval` в `landing-final-check.sh`

### Кластер E — Verifier hygiene
- [ ] `verify-composed-premium.sh` parallax regex слишком широкий
- [ ] `verify-composed-has-visuals.sh` placeholder regex слишком узкий (`[ICON:`, `[CHART:` не ловится)
- [ ] `verify-visual-qa.sh` — orphan (нигде не вызывается)
- [ ] `verify-composed-premium` чекает только 13 фич из 20 (по CLAUDE.md)
- [ ] verify-скрипты без `set -e`

### Кластер F — Correctness bugs (среднего риска)
- [ ] `flush.py:88` swallows SDK errors silently
- [ ] `hash_cache.py:19` corrupt cache → mass token cost
- [ ] `hash_cache.py` non-atomic write
- [ ] `cleanup_broken_links.py:42` non-atomic write
- [ ] `verify_photo_pipeline.py._find_block_meta` per-img walk
- [ ] `session_end.py`/`pre_compact.py` trust stdin `transcript_path` без allowlist

---

## Позитивы (это работает — не трогать)

Хорошие паттерны, которые надо **тиражировать**, а не править:

1. **`photo-curator`, `block-composer`, `ux-composer`, `photo-stylist`** — открываются явным `STRICT/CRITICAL CONSTRAINT` блоком с запрещёнными действиями и verify-скриптом. **Эталонный паттерн для всех остальных агентов** (см. фикс #2).
2. `utils.atomic_write` используется консистентно в Python.
3. **Документированное решение перестать использовать SDK для генерации индекса** (заменено на детерминированный stub) — ровно правильное движение.
4. Late imports в `compile.py` держат CLI startup быстрым.
5. `niche-analyst` `[ДОПУЩЕНИЕ]` convention — сильная anti-fabrication дисциплина.
6. Чистые exit-code конвенции в свежих verify-скриптах.
7. NUL-safe `find -print0`.
8. Mermaid pipeline-map авто-write — умный UX.
9. `premium-07b-checklist.md` — топ-документация с reference-implementation.
10. `gate-check.sh` хорошо структурирован и data-driven из YAML (когда не падает на legacy-bypass).

---

## Рекомендуемый порядок исполнения

**Фаза 1 — Quick wins (1 день):**
Фиксы #3, #4, #5, #6, #7, #8 из Top-10. Это самые дешёвые правки с максимальным эффектом. Каждая по 5-30 минут.

**Фаза 2 — Enforcement hooks (1 день):**
Фикс #1 (`PreToolUse` hook) + Cluster A целиком. Это превращает декоративные правила в физический закон.

**Фаза 3 — Agent hygiene (1 день):**
Фиксы #2, #9, #10 + Cluster B. Тиражирование эталонного `STRICT CONSTRAINT` паттерна.

**Фаза 4 — Token efficiency (опционально):**
Cluster C. После фазы 1 базовая утечка уже закрыта. Здесь — донастройка.

**Фаза 5 — RAG decision gate:**
Замерить токены до/после фаз 1-4. Решить — нужен ли RAG или система уже летает.

---

## Что НЕ нужно делать

- ❌ Mass-рефакторинг — структура хорошая, ломать не надо
- ❌ Переписывание агентов с нуля — преамбулы достаточно
- ❌ Замена `gate-check.sh` на новую систему — починить эту
- ❌ Внедрение RAG до завершения фазы 4 — рано, эффект неизмерен
