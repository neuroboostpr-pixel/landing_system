# Audit 03 — Agents / Skills / Commands (prompt-as-code review)

**Scope:** 33 agent files in `agents/*.md`, 24 skill `SKILL.md` files in `skills/*/`, 27 command files in `commands/*.md` + 25 in `.claude/commands/*.md`.

**Methodology:** Adapted `code-reviewer/SKILL.md` workflow to prompt review. Critical/Major/Minor/Positive/Verdict template. For skip-the-step loopholes the exact problematic sentence is quoted and a replacement is proposed. Every script path referenced in an agent or command was cross-checked against `scripts/` and `skills/*/scripts/` for existence.

**Pipeline assumption (per `CLAUDE.md`):** `Stage Execution Protocol` from `docs/standards/stage-execution-protocol.md` is mandatory before every stage action; HARD GATE 07b is enforced by `scripts/verify-composed-premium.sh`; PR-D `landing-orchestrator` integration is **done** (not a TODO).

---

## Summary

One-sentence intent recap: This system uses markdown prompts as code to orchestrate a 12-stage landing pipeline, and the agent prompts MUST enforce the pipeline strictly because the orchestrator delegates trust to each sub-agent.

Overall assessment: The agents in the **primary pipeline path** (`landing-orchestrator`, `block-composer`, `ux-composer`, `photo-curator`) are reasonably hardened with explicit HARD GATEs and verify-script references. The **secondary agents** (Phase 2/3 agents like `analytics-engineer`, `integrations-engineer`, `seo-optimizer`, `wp-deployer`, `brand-architect`, `qa-auditor`, `style-extractor`, etc.) lack the Stage Execution Protocol preamble entirely — they don't read `.landing-state.yaml`, don't call `gate-check.sh`, and don't reference `docs/standards/stage-execution-protocol.md`. Eight commands and several agents still carry **stale "PR-D not done" / "integration is a TODO" notes** that contradict `CLAUDE.md`. There are 4 broken cross-references (paths to files that don't exist where the agent expects them). The pipeline can be skipped at multiple points if an agent is invoked directly.

---

## Critical issues — must fix before relying on agents to enforce the pipeline

### C1. Stage Execution Protocol is only inside `landing-orchestrator.md` — every other stage agent can skip it

`CLAUDE.md` makes the protocol mandatory: "Перед ЛЮБЫМ действием на этапе агент обязан: (1) прочитать `.landing-state.yaml` и показать Mermaid-карту..., (2) выписать все оставшиеся этапы в TodoWrite, (3) подгрузить `stage-<id>-checklist.md`, (4) verify → approve." Only `agents/landing-orchestrator.md` has this preamble. The following stage-owner agents have **no Stage Execution Protocol section at all** and no `gate-check.sh` call:

- `agents/brand-architect.md` (stage 04)
- `agents/design-system-generator.md` (stage 05)
- `agents/stack-planner.md` (stage 06)
- `agents/content-writer.md` (stage 07)
- `agents/wp-builder.md` (stage 08)
- `agents/integrations-engineer.md` (stage 08)
- `agents/analytics-engineer.md` (stage 08)
- `agents/seo-optimizer.md` (stage 08)
- `agents/wp-deployer.md` (stage 09)
- `agents/qa-auditor.md` (stage 10)
- `agents/style-extractor.md`, `references-curator.md`, `moodboard-composer.md`, `scene-director.md`, `client-assets-collector.md` (earlier stages)

Concrete effect: if a user (or another agent) calls e.g. `wp-builder` directly via Task tool — or if `landing-orchestrator` delegates to it — `wp-builder` will happily run without reading state, without TodoWrite, and without `gate-check.sh`. The orchestrator's discipline is irrelevant if the sub-agent doesn't enforce its own gate.

**Fix:** Add a uniform 5-line preamble at the top of EVERY stage-owner agent file (after frontmatter):

```markdown
## Stage Execution Protocol (обязательно)

Перед ЛЮБЫМ действием выполнить шаги 1–4 из [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md):

1. `bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki` — показать карту пользователю.
2. TodoWrite со всеми оставшимися этапами от `current_stage`.
3. `bash scripts/gate-check.sh --stage <my_stage_id> --project <project>`. Если exit ≠ 0 — STOP, не работать.
4. После завершения и approve пользователя: `bash scripts/gate-check.sh --stage <my_stage_id> --project <project> --approve`. Без approve не объявлять этап завершённым.
```

This is a five-line copy/paste, but it is the single highest-leverage change in the whole prompt corpus.

### C2. `landing-orchestrator.md` describes "Phase 1 Scope" as still-current behavior — agents will think old flow is authoritative

`agents/landing-orchestrator.md` lines 61–67:

> ## Phase 1 Scope (текущая реализация)
>
> В Phase 1 я умею **только**:
> 1. Принимать контроль после `landing-project-init` или `landing-from-context`.
> 2. Спрашивать пользователя: ниша / клиент / KPI / есть ли прототип / есть ли материалы клиента.
> 3. Заполнять `00_БРИФ/brief.md` на основе ответов.
> 4. Сообщать: «Phase 1 завершён. Этапы 02–12 будут доступны после Phase 2 implementation».

Phases 2/3/4/5 follow with similar "current limitation" framing. But `CLAUDE.md` says PR-D is done and `/landing-go` is the main entry. The "Phase 1 Scope" block reads to an LLM as the authoritative current capability, not legacy doc. Two things can happen:

1. Orchestrator literally says "Phase 1 завершён. Этапы 02–12 будут доступны после Phase 2 implementation" when called on a brand-new project — false to user.
2. Orchestrator self-limits to brief gathering and refuses to continue past stage 00.

Both have happened in similar prompt systems. The file even contradicts itself: line 245 onwards has "PR-D Phase" with a new dispatch table that supersedes Phase 1.

**Fix:** Delete or move the Phase 1–5 Scope sections to a clearly-labeled `## Legacy (do not follow)` archive at the bottom, and promote the "PR-D Phase: Prototype-First Orchestration" section to top of file (right after Stage Execution Protocol). The current dispatch table starts at line 256; that's the real one.

### C3. `landing-compose.md`, `landing-photos.md`, `landing-visuals.md`, `landing-wireframe.md`, `landing-prototype.md` all say "не интегрировано в landing-orchestrator — задача PR-D"

`CLAUDE.md` says PR-D is done. All five PR-A/B/C command docs in `commands/` still carry the stale note:

- `commands/landing-compose.md:28` — `Не интегрировано в landing-orchestrator — задача PR-D.`
- `commands/landing-photos.md:65–66` — `PR-B команда вызывается вручную, не через landing-orchestrator. Полная интеграция в orchestrator + config/stage-gates.yaml — задача PR-D.`
- `commands/landing-visuals.md`, `landing-wireframe.md`, `landing-prototype.md` — similar.

Effect: an LLM reading these will refuse to dispatch them from `/landing-go`, or will tell the user "this isn't integrated yet" — false. Either ship PR-D and update the docs, or leave PR-D unshipped — but `CLAUDE.md` and these command files cannot disagree.

**Fix:** Either (a) delete the "## NOTE (PR-X scope)" block from each of those 5 command files (they're now integrated), or (b) revert `CLAUDE.md` to admit PR-D is partial. Recommend (a) — replace each NOTE with one line: `Под капотом вызывается из /landing-go (см. agents/landing-orchestrator.md, dispatch table PR-D).`

### C4. Broken file references in 3 agents

These paths are referenced as prerequisites/inputs but the file does not exist where expected:

1. **`agents/integrations-engineer.md:16`** — lists `08_КОД/acf-fields.json` as prerequisite. But `agents/wp-builder.md:106` explicitly states: `Не создаётся: ... acf-fields.json — это артефакты прежней ACF-Blocks эпохи.` Lazy Blocks replaced ACF. **Fix:** Replace the line `08_КОД/acf-fields.json содержит поле form_id для секции form` with `08_КОД/block-spec.yaml содержит блок form с полем form_id`.

2. **`agents/seo-optimizer.md:17, 22`** — reads `00_БРИФ/approved-design-brief.md`. Template only has `00_БРИФ/brief.md` (verified via `ls template/00_БРИФ/`). The `approved-design-brief.md` is a ghost — no upstream agent writes it. **Fix:** Change both occurrences to `00_БРИФ/brief.md`.

3. **`agents/content-writer.md:18, 39`** — reads `07_КОНТЕНТ/prototype.md`. Actual location is `07_ПРОТОТИП/prototype.md` (written by `prototype-importer`, verified via `template/07_ПРОТОТИП/` and `template/07_КОНТЕНТ/` — the latter only has `README.md`). **Fix:** Replace `07_КОНТЕНТ/prototype.md` → `07_ПРОТОТИП/prototype.md` in both places.

4. **`agents/prototype-importer.md:21–26`** — promises that "после конвертации md→yaml конвейер автоматически запускает `enrich-quiz-funnel.py`" but the script lives in `skills/wireframe-rendering/scripts/enrich-quiz-funnel.py`, not in `skills/prototype-import/scripts/`. The agent itself doesn't call it (the workflow only invokes `md-to-yaml.py` + `validate-prototype.py` at steps 6–7), so the promised behavior is also unimplemented. Also the workflow says "если quiz блок есть, расширится в полный Marquiz-фаннел" but no instruction makes that happen. **Fix:** Either remove the misleading paragraph, or add an actual step 6.5 that calls the right script path.

### C5. `landing-orchestrator.md` claims old-flow Stage 02 / Stage 04 agents exist, but in PR-D mode stages 00/01/01a/02 are marked `n/a`

Lines 91–108 give detailed Stage 02 and Stage 04 dispatch flows. Line 251 (PR-D section) says these stages are `n/a`. An LLM following the orchestrator may start spinning up `client-assets-collector` and `photo-stylist` even though state has them marked `n/a`. The Phase-2 dispatch tables should be removed (legacy) or guarded by an explicit `if state.yaml stages.02_assets.status != "n/a"` instruction.

**Fix:** Add an explicit guard at the top of every per-phase dispatch block, e.g.:

```
**Только если `.landing-state.yaml:stages.<stage_id>.status` != `n/a` или `skipped`. В prototype-first режиме этап помечен `n/a` — не запускать агентов этой фазы.**
```

---

## Major issues — should fix before next pipeline run

### M1. Skip-the-step loopholes (quoted, with replacement wording)

**M1a — `agents/qa-auditor.md:25`** quote:

> 1. Читаю `00_БРИФ/brief.md` — нахожу URL сайта.

Loophole: no instruction to call `gate-check.sh --stage 10_qa` first; no instruction to verify stage 09_deploy is `approved`. The QA agent can run against a non-deployed URL or a stale deploy.

Replacement: prepend a Pre-flight block:
```markdown
## Pre-flight (обязательно)

1. `bash scripts/gate-check.sh --stage 10_qa --project <project>` — если exit ≠ 0, STOP.
2. Прочитай `<project>/.landing-state.yaml:stages.09_deploy.status` — если != `approved`, отказаться: «Сначала утверди этап 09 (деплой).»
3. Только после этого читай brief.md.
```

**M1b — `agents/wp-deployer.md:23`** quote:

> 6. **HARD GATE**: показываю URL сайта, жду утверждения.

Loophole: HARD GATE here is "show URL, wait for utверждения" but there's no instruction to run `bash scripts/gate-check.sh --stage 09_deploy --project <project> --approve` after the user approves. The state file will never advance.

Replacement: after step 6 add:
```markdown
7. После «утверждаю»: `bash scripts/gate-check.sh --stage 09_deploy --project <project> --approve`. Без этой команды state.yaml не обновится и QA-этап (10) не разблокируется.
```

**M1c — `agents/photo-stylist.md:30, 36`** quote (step 2):

> 2. For each photo, ask user about intended use (hero / about / proof).

Loophole: in a Stage 02 batch, a user with 80 photos will be asked 80 questions. The agent has no instruction to batch ("ask for groups" or "use AI classification") and no instruction to abort if user goes silent. Combined with the open-ended HARD GATE at line 38 ("user reviews assets-gallery.html"), the agent can hang indefinitely.

Replacement:
```markdown
2. Если фоток >5 — НЕ спрашивай по каждой. Просьба: «Загрузи в подпапки: hero/, about/, proof/. Напиши готово.» Затем обрабатывай батчами по 20.
```

Also tighten the HARD GATE: explicitly say "получи слово 'утверждаю' / 'ok' / 'дальше' — иначе не вызывать gate-check --approve".

**M1d — `agents/visual-curator.md:14–18`** Hard prerequisites are correct, but the comparison string is wrong:

> `<project>/.landing-state.yaml:stages.05_design.status == approved`

This is documenting how to gate, but never instructs the agent to actually run `gate-check.sh`. The agent compares string-equality to `approved` manually. Stage names also differ from the canonical IDs in `config/stage-gates.yaml` (`05_design` is fine, but the agent never reads that config). Similar in `agents/photo-curator.md:38–42`.

Replacement: replace manual yaml check with a script call:
```markdown
1. `bash scripts/gate-check.sh --stage 07d_visuals --project <project>`. Если exit ≠ 0 — STOP, передай вывод пользователю.
```

**M1e — `agents/brand-architect.md:23–25`** quote:

> 1. Run `python3 skills/brand-kit-build/scripts/build.py <project-dir>` — produces `04_БРЕНД/brand-kit.md`
> 2. Run `python3 skills/brand-kit-build/scripts/render-html.py <project-dir>` — produces `04_БРЕНД/brand-kit.html`
> 3. Open `04_БРЕНД/brand-kit.html` for user review.

Step 3 says "Open" — ambiguous. An LLM may interpret as `Read` tool call (token waste) or as a `Bash` `open`. No HARD-GATE-with-approve at the bottom either; just a vague "Don't proceed... until user approves" prerequisite. No `gate-check.sh --approve` instruction.

Replacement: rewrite step 3 + add explicit gate-close:
```markdown
3. Сообщи пользователю путь `04_БРЕНД/brand-kit.html` и попроси открыть его двойным кликом. НЕ читай HTML сам через Read — это трата токенов, превью предназначено для пользователя.
4. После явного approve от пользователя: `bash scripts/gate-check.sh --stage 04_brand --project <project> --approve`.
```

**M1f — `agents/stack-planner.md:44`**:

> 8. **HARD GATE**: показываю пользователю design-stack.yaml, жду утверждения.

Same pattern: no `--approve` call. Same fix as M1e.

**M1g — `agents/design-system-generator.md:20`**:

> 6. **HARD GATE**: жду явного утверждения (`утверждаю`, `ok`, `дальше`) перед переходом к этапу 06.

Better than most (lists trigger words) but still no `gate-check.sh --approve` call. Same fix.

**M1h — `agents/seo-optimizer.md:56`**, **`agents/analytics-engineer.md:51`**, **`agents/integrations-engineer.md:41`**:

All three end with `**HARD GATE**: показываю ..., жду утверждения` and never invoke `--approve`. None of these stage-08 sub-agents run a gate-check at all.

Replacement: add a single Pre-flight + Post-completion block to each (3 minutes of editing, but it's mandatory for the gate state machine to function).

### M2. `frontend-builder.md` has "ZERO-JS by default" and "if you think JS is required... leave TODO" — escape hatch the agent can rationalize

quote:

> Zero JS — use `<details>`/`<summary>` for accordions, `position: sticky` + CSS for sticky CTAs, checkbox-hack or `<details>` for mobile burger.
> ...
> `assets/js/*` (zero-JS by default; if you believe JS is required, leave a `// TODO: needs JS — discuss with manager` comment in `block.php`, do not write JS).

LLMs love "if you believe X is required" — that's an open invitation to fall back. Counter-evidence: 90% of premium-07b-checklist requires JS (count-up via rAF, lightbox keyboard navigation, slider). The orchestrator's HARD GATE 07b will fail if JS is missing, but `frontend-builder` (stage 08b) operates AFTER 07b is closed — so the contradiction is silent.

Replacement: state explicitly that JS for premium-07b features lives in `08_КОД/wp-theme/assets/js/main.js` and is written by `wp-builder` / `landing-build` Step 8, not by frontend-builder. Reframe the "zero-JS" rule to apply only to per-block markup, not to global animation/slider/lightbox.

### M3. `wp-builder.md` reads paths that don't exist for prototype-first projects

quote (lines 19–21):

> - `01a_АНАЛИЗ_НИШИ/landing-structure.md` — список блоков лендинга...
> - `01a_АНАЛИЗ_НИШИ/market-profile.md` — для адаптации поведения блоков
> - `01a_АНАЛИЗ_НИШИ/positioning.md` — заголовок `**Mode:** <режим>` определяет приоритеты блоков.

In PR-D prototype-first mode, stage 01a is `n/a` and these files don't exist. `landing-orchestrator.md:258` partially compensates with a "Bridge: prototype → landing-structure.md via `scripts/derive-landing-structure.py`" — but `wp-builder.md` doesn't mention this bridge and will fail to read `positioning.md` and `market-profile.md` if they were never generated.

Replacement: add to `wp-builder.md` Prerequisites section:
```markdown
**Если этап 01a помечен `n/a` (prototype-first mode):**
- `landing-structure.md` создаётся через `bash scripts/derive-landing-structure.py <project>` (выполняется оркестратором перед запуском wp-builder).
- `market-profile.md` / `positioning.md` могут отсутствовать — в этом случае Mode-aware behavior и accessibility-tier behavior работают в `legacy_v1` режиме (без augmentation). Не падать.
```

### M4. `prototype-importer.md` "если что-то непонятно — спроси" without batching cap

quote line 50:

> 5. **Если что-то непонятно — спроси у пользователя:**
>    - какая ниша (services / b2c / local)?
>    - block #N не определился — это hero, features, или что?

For a 20-block prototype, this becomes 20 sequential questions. Add: "Группируй все вопросы в одно сообщение. Не более одного раунда вопросов на запуск."

### M5. `niche-analyst.md` step 5 mass-scrapes 15–25 competitors via `mcp__firecrawl__scrape` — no rate-limit guardrails, no skip-on-fail

quote line 62:

> ### Шаг 5. Скрейп каждого конкурента
> Через `mcp__firecrawl__scrape`. Извлечь: positioning (h1/hero), key_messages (выделенные блоки), price_range, target_audience, visual_notes.

Failure modes: Firecrawl API quota exhaustion, single broken site hanging the whole batch, no caching. Should specify: "Скрейпи последовательно. На каждом конкуренте — try/catch; при ошибке пиши `scrape_status: failed` в его записи и продолжай. После 3 подряд провалов — STOP, спроси пользователя продолжать или нет."

### M6. `landing-onboarding-wizard.md` Phase 4 ШАГ 2 says "если фоток нет — напиши «пропустить» (я сгенерю через AI)"

quote line 108:

> Если фоток нет — напиши "пропустить" (я сгенерю через AI).

The wizard itself doesn't generate photos. The actual generation happens way later in `photo-curator` / `photo-preview-board`. The user may put off providing photos thinking it's free, then hit unexpected codex bills at stage 07c. Replacement:

> Если фоток нет — напиши "пропустить". На этапе 07c (photo pipeline) для пустых слотов будут SVG-плейсхолдеры или AI-генерация (требует явного согласия и стоит ~$0.05/слот).

### M7. `photo-classifier.md` and `photo-matcher.md` retry strategy: "retry 2x with stricter prompt, then fall back to `tags: [unclassified]`"

For 50 photos with 5% codex-flake rate = 2–3 unclassified at minimum. The matcher will then receive an `unclassified` photo and try to rank it against slot hints, with no instruction what to do (probably ignore). Result: silent skipped photos. Fix: matcher must explicitly skip `unclassified` photos and surface them to user at the end: "X фото остались unclassified — открой 07c_PHOTOS/photo-board.html, расставь руками или удали."

### M8. `seo-optimizer.md` hardcodes `Schema.org @type LocalBusiness` in the example PHP

quote line 45:

> `{"@context":"https://schema.org","@type":"LocalBusiness","name":"..."}`

But line 64 lists alternatives (Course, Organization). The example PHP is the most likely thing an LLM will copy. It should be templated by niche from `market-profile.md`. Replace the hardcoded JSON with: `<TYPE из market-profile §1 accessibility_tier маппинга>`.

---

## Minor issues — nice to have

### Mn1. Frontmatter `description:` quality varies

Bad (too vague — Claude Code can't tell when to invoke):
- `agents/lifecycle-keeper.md`: `Manages landing versions (snapshots), rollbacks, and A/B clones. Used by /landing-rollback and /landing-clone.` (fine, has triggers)
- `agents/icon-generator.md`: `Generates ONE icon PNG via codex image_gen for a given slot.` (fine)
- `agents/style-extractor.md`: `Use during stage 04 after moodboard is approved...` (fine)

Bad — could be triggered too broadly:
- `agents/scene-director.md`: starts with `Use during stage 05 (cinematic mode only)...` — good gating
- `agents/lifecycle-keeper.md` — actually fine

Strong examples to imitate:
- `agents/niche-analyst.md` — long, lists exact triggers, says "Zero-touch".
- `agents/photo-curator.md` — names the slash command that triggers it.

All `agents/*.md` should follow the niche-analyst pattern: stage id + when to invoke + which slash command triggers it + identity-safe rules if any.

### Mn2. Several agents use `Bash, Read, Write, Edit, Glob` without an `allowed-tools:` line

Comparing frontmatter:
- `agents/wp-builder.md` has `allowed-tools: Bash, Read, Write, Edit` (good)
- `agents/landing-orchestrator.md`, `block-composer.md`, `ux-composer.md`, `photo-curator.md`, `visual-curator.md`, `prototype-importer.md`, `landing-onboarding-wizard.md` have **no `allowed-tools:`** in frontmatter — they list tools in a `## Tools` section in the body. Claude Code's frontmatter parser will read `allowed-tools` only from frontmatter, not from a `## Tools` body section. This means these agents may inherit too-broad tool access (or, depending on Claude Code's defaults, may even include WebSearch / `mcp__*` they don't need).

Fix: hoist the `## Tools` lines into frontmatter `allowed-tools:` keys.

### Mn3. `landing-style.md` command lives only in `.claude/commands/` not in `commands/`

`commands/landing-style.md` does not exist; `.claude/commands/landing-style.md` does. All other commands have a copy in both directories. Either add `commands/landing-style.md` or document why one command is `.claude/`-only.

### Mn4. `landing-orchestrator.md` ASCII diagram of stages duplicates / contradicts `template/` folder names

Lines 51–60 use mixed naming: stage "05" maps to `05_ДИЗАЙН-СИСТЕМА` in template, but text says "Дизайн-система". The PR-D dispatch table further down uses `05_design` IDs. Three different naming schemes coexist (Russian template names, English IDs, Russian Cyrillic state.yaml keys). At minimum add a one-line mapping table at the top.

### Mn5. `agents/ux-composer.md` requires **11** files to be injected into context

Lines 13–27 require pre-flight injection of: prototype.yaml, tokens.json, brand-kit.md, catalog.yaml, 5 CSV files from ui-ux-pro-max, 2–3 DESIGN.md references. That's potentially 100KB+ of context for a single agent invocation. Items 5–10 (CSV files) are already injected by `render-wireframe.py` according to line 28. The agent's own context injection is redundant.

Fix: rewrite section as:
```markdown
## CRITICAL — pre-flight injection contract

Перед началом работы прочитай ТОЛЬКО:
1. `<project>/07_ПРОТОТИП/prototype.yaml`
2. `block-library/catalog.yaml`

Все остальные данные (ui-ux-pro-max CSVs, brand-kit, tokens) подгрузит `render-wireframe.py` автоматически в HTML. Не читай эти файлы из агента — это трата токенов.
```

### Mn6. `block-composer.md` lines 80–86 — pre-flight reads `meta.yaml` for "every chosen block", optionally consults `~/.claude/skills/ui-ux-pro-max/data/styles.csv`

quote line 86:

> Это необязательно блокирующий шаг — если styles.csv не доступен, пропустить.

"необязательно блокирующий" — exactly the kind of "use your judgment" phrase that lets agents skip. Either it's required (then say "STOP if missing"), or it's a nice-to-have (then say "if file missing, skip silently and proceed"). Don't leave both reads open.

### Mn7. `agents/landing-orchestrator.md` line 320 has a typo / loose phrasing

> «🎯 Открой 07a_WIREFRAME/wireframe.html, выбери варианты, скачай selections.yaml. Напиши готово»

User-facing copy mixed with prompt instruction. Move user-prompts into a dedicated `## User-facing messages` block so an LLM doesn't reproduce them verbatim every time and so they're a single source of truth.

### Mn8. `agents/wp-builder.md` Visual sanity-checks (lines 117–124) read `01a_АНАЛИЗ_НИШИ/visual-requirements.md` Sections 1, 4, 5

If 01a is `n/a`, these checks silently no-op. Need an explicit fallback rule: "Если visual-requirements.md отсутствует, пропустить sanity-check и записать warning в build log."

### Mn9. `landing-build.md` has 11 steps; steps 2–4 and 8–10 overlap

Step 2 invokes `integrations-engineer`. Step 10 runs `generate-integrations.py`. Step 3 invokes `analytics-engineer`. Step 9 runs `generate-analytics.py`. Either the AI agents are deterministic-equivalent to the scripts (then drop the agents), or they're different (then docs need to explain). Today: a user reads the command file and can't tell.

### Mn10. `commands/landing-content.md:25` reads "prototype.md" from same wrong path as content-writer agent

> 2. Read `07_КОНТЕНТ/prototype.md` and block structure from `DESIGN.md`.

Same C4-#3 fix applies here.

---

## Positive feedback — patterns worth replicating

- **P1.** `agents/photo-curator.md` opens with an explicit `## ОБЯЗАТЕЛЬНО: codex post-process для каждой фотки (PR-I.a)` block listing forbidden actions and the HARD GATE script (`verify-photo-pipeline.sh`). This is the gold-standard format for "agent that owns a stage" — copy this structure to all stage-owner agents.

- **P2.** `agents/block-composer.md` opens with `## СТРОГО: контент прототипа неприкосновенен (PR-H)` and quotes the actual verify script. The "Если хочешь что-то изменить — НЕ делай этого молча, спроси пользователя явно" instruction is exactly the kind of explicit anti-loophole language that other agents lack.

- **P3.** `agents/ux-composer.md` lines 36–42 — "Если файл отсутствует — ОСТАНОВИСЬ и сообщи пользователю" with exact install command. Excellent skip-resistant pattern.

- **P4.** `agents/photo-stylist.md:34` — the "CRITICAL CONSTRAINT — only style.py" paragraph is exemplary anti-workaround language: "You may ONLY invoke ... Do NOT use any other image tooling ... If you think you need a different operation, STOP and ask the user — don't invent a workaround." Every identity-safe / data-integrity agent should have a paragraph like this.

- **P5.** `agents/niche-analyst.md` `[ДОПУЩЕНИЕ]` + `confidence: low/medium` convention — explicit gap-marking instead of fabrication. Strong.

- **P6.** All `commands/landing-*.md` that are post-onboarding (`landing-build`, `landing-content`, `landing-design`, `landing-brand`, `landing-stack`, `landing-references`, `landing-moodboard`, `landing-deploy`) have a uniform `## Pre-flight` block that runs `setup-flag.sh is_complete` and `gate-check.sh --stage X` and a uniform `## Post-completion` block that runs `--approve`. This is the right pattern. The agents themselves (C1) should mirror this — currently only the command wrappers enforce it, which means direct agent invocation bypasses both.

- **P7.** `agents/landing-orchestrator.md` lines 291–308 PR-H content-preserve / Premium 07b enforcement section: "**«И так сойдёт» — недопустимо.**" Specific, named anti-pattern. More agents should copy this style.

- **P8.** `scripts/` is **clean**: every script referenced from agents resolves (with the 1 PR-I.a exception in C4). Major win — most prompt corpora have 5–10× more dead refs.

---

## Questions for author

1. Is **PR-D actually shipped**? `CLAUDE.md` says yes. Five command files say no. Single source of truth needed.
2. Are stages 00/01/01a/02 always `n/a` in prototype-first mode, or only sometimes? `landing-orchestrator.md` and `landing-go.md` disagree subtly (`landing-go.md:24` is unconditional; `landing-orchestrator.md:251` qualifies it with "Этапы помечены `n/a`").
3. Is `frontend-builder` a real stage 08b agent, or part of `wp-builder`? It's not in the orchestrator's PR-D dispatch table, but `commands/landing-style.md` (in `.claude/commands/` only) implies it is.
4. Does `niche-analyst` get called from `landing-go` at all? Stage 01a is `n/a` in prototype-first, and `landing-niche.md` is a separate manual command. Confirm there is no orphan path.

---

## Verdict

**Request Changes.**

The pipeline as written has 1 systemic bug (C1 — only orchestrator enforces Stage Execution Protocol), 1 self-contradiction (C2/C3 — Phase 1 Scope and "PR-D not done" notes vs PR-D shipped claim in CLAUDE.md), 4 broken file refs (C4 — acf-fields.json, approved-design-brief.md, 07_КОНТЕНТ/prototype.md ×2, enrich-quiz-funnel.py path), and ~8 skip-the-step loopholes (M1a–h) where an agent can mark a stage "done" without ever calling `gate-check.sh --approve` and thus the state machine never advances.

Highest-leverage single change: **C1's 5-line preamble copy/pasted into every stage-owner agent** would close 80% of the loophole surface and force the pipeline to be self-enforcing rather than orchestrator-dependent.

Estimated effort: 2–3 hours of editing for C1 + M1; 1 hour for C2/C3 doc reconciliation; 30 min for C4 path fixes. Total ~4 hours to bring agents to "strictly enforce pipeline" baseline.

---

## Cross-reference verification summary

Scripts verified to exist: 51/52 referenced paths resolve. **One miss:** `enrich-quiz-funnel.py` is referenced in `agents/prototype-importer.md` as `skills/prototype-import/scripts/enrich-quiz-funnel.py` but actually lives at `skills/wireframe-rendering/scripts/enrich-quiz-funnel.py`. The agent doesn't actually invoke the script — only describes it as "автоматически запускается" in narrative prose — so this is a documentation lie rather than a runtime crash.

Files verified to exist: `docs/standards/stage-execution-protocol.md`, `docs/standards/premium-07b-checklist.md`, `config/stage-gates.yaml`, `config/positioning-modes.yaml`, `config/niche-visual-rules.yaml`, `docs/SETUP.md`, `template/08_КОД/block-spec.example.yaml`, `vendor/opendesign-extracts/design-systems-refs/`, `skills/photo-curation/IDENTITY_SAFE.md` — all resolve.

Files NOT verified to exist (referenced but not at expected path):
- `00_БРИФ/approved-design-brief.md` — never created by any agent. Used by `seo-optimizer.md`.
- `08_КОД/acf-fields.json` — explicitly NOT created (Lazy Blocks era). Used by `integrations-engineer.md` prereqs.
- `07_КОНТЕНТ/prototype.md` — actual path is `07_ПРОТОТИП/prototype.md`. Used by `content-writer.md` and `commands/landing-content.md`.

---

## Files reviewed (absolute paths)

Agents (33):
`/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/agents/landing-orchestrator.md`,
`block-composer.md`, `ux-composer.md`, `wp-builder.md`, `photo-curator.md`, `niche-analyst.md`, `brand-architect.md`, `content-writer.md`, `design-system-generator.md`, `qa-auditor.md`, `wp-deployer.md`, `visual-curator.md`, `prototype-importer.md`, `landing-onboarding-wizard.md`, `frontend-builder.md`, `seo-optimizer.md`, `analytics-engineer.md`, `client-assets-collector.md`, `integrations-engineer.md`, `onboarding-guide.md`, `photo-classifier.md`, `photo-matcher.md`, `photo-preview-board.md`, `photo-stylist.md`, `icon-generator.md`, `infographic-builder.md`, `lifecycle-keeper.md`, `moodboard-composer.md`, `references-curator.md`, `scene-director.md`, `stack-planner.md`, `style-extractor.md`, `system-setup.md` (all under `agents/`).

Skill SKILL.md files (24): all under `skills/*/SKILL.md` (block-composition, block-library-management, brand-kit-build, client-assets-collection, design-tokens-generation, gpt5-prompting-engine, landing-from-context, landing-onboarding, landing-project-init, landing-versioning-and-cloning, moodboard-creation, niche-analysis, paralaximus-codex, photo-curation, photo-styling, prototype-import, references-collection, style-decomposition, visual-generation, visual-qa, wireframe-rendering, wp-cli-deployer, wp-gutenberg-block-builder, wp-theme-assembler).

Commands (52 across two dirs): all under `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/commands/*.md` and `/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system/.claude/commands/*.md`.
