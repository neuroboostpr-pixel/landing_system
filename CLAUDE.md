# Landing System — CLAUDE Instructions

Это папка мастер-системы для производства WordPress-лендингов через Claude Code.

## Что это

Агентская система для построения production-grade лендингов на WordPress + Бегет.
Полный цикл: бриф → мудборд → бренд-кит → DESIGN.md → код → деплой → QA → SEO.

## Главные команды

- `/landing-new <slug>` — создать новый проект-лендинг с нуля
- `/landing-from-context <slug>` — создать проект из родительской папки агентства
- `/landing-status` — статус системы и текущих проектов
- `/landing-help` — справка по всем командам

## Новые команды PR-A (Прототип + Wireframe + Compose)

- `/landing-prototype` — импорт пользовательского прототипа (PDF/MD) → prototype.{md,yaml}
- `/landing-wireframe` — интерактивный wireframe.html с 2-3 вариантами на блок
- `/landing-compose` — composed.html с tokens + текстами, placeholders для визуала

**Workflow PR-A:**
1. Положи `prototype.pdf` или `.md` в `<project>/07_ПРОТОТИП/source/`
2. Запусти `/landing-prototype` → проверь `prototype.md`, поправь если нужно
3. Запусти `/landing-wireframe` → открой `07a_WIREFRAME/wireframe.html`, выбери варианты, нажми «Confirm» — скачается `selections.yaml`, положи его в `07a_WIREFRAME/`
4. Запусти `/landing-compose` → `07b_COMPOSED/composed.html` готов

**NOTE:** PR-A команды вызываются ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция в оркестратор — задача PR-D.

## Новые команды PR-B (Photo Pipeline)

- `/landing-photos` — обработка клиентских фоток: AI-classify через codex, matching к слотам, generative fallback для пустых слотов. **Stage 07c.**

**Workflow PR-B:**
1. Утверди этапы 05 (design-system) и 07a (wireframe).
2. Положи фотки клиента в `<project>/07c_PHOTOS/inbox/`. Подсказка: открой `07c_PHOTOS/README.md` — там описаны 7 подпапок по типу фото (`портреты_и_команда/`, `процесс_работы/` и т.д.).
3. Запусти `/landing-photos`.
4. Открой `07c_PHOTOS/photo-board.html` — расставь фотки drag-drop, нажми «Подтвердить и скачать selections.yaml».
5. Положи скачанный `selections.yaml` обратно в `07c_PHOTOS/`.
6. Открой `07c_PHOTOS/photo-preview.html` — проверь как фото лягут в макет.
7. После approve — `composed.html` перерендерится с реальными фото (placeholders заменятся на `<img>` или `<picture>` с mobile-вариантом).

**Идентичность-safe:** клиентские фото никогда не репеинтятся AI; AI-генерация лиц для testimonial/expert/team слотов требует явной галочки `ai_approved_by_user`.

**NOTE:** PR-B команда вызывается ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция в orchestrator + stage-gates — задача PR-D.

См. [spec](docs/superpowers/specs/2026-05-13-photo-pipeline-design.md) и [plan](docs/superpowers/plans/2026-05-13-photo-pipeline-plan.md).

## Новые команды PR-C (Visual Generation)

- `/landing-visuals` — AI-генерация иконок и инфографики через codex image_gen. **Stage 07d.**

**Workflow PR-C:**
1. Утверди этап 05 (design-system) и убедись что есть `07b_COMPOSED/composed.html` (PR-A).
2. Запусти `/landing-visuals`. Без флагов = и иконки, и инфографика.
3. Codex генерит PNG под брендинг (цвета из `tokens.json`, ниша из `market-profile.md`).
4. Кэш по hash(hint + style + brand_color + niche) — повторный прогон НЕ зовёт codex для тех же слотов.
5. `composed.html` перерендерится — placeholders `[SLOT: feature-1-icon]` заменятся на `<img class="lp-icon">`.

**Опциональные флаги:**
- `--type icons` или `--type infographics` — частичный прогон
- `--force` — игнорировать кэш
- `--slot <name>` — один конкретный слот

**Identity-safe** НЕ применяется (в иконках/чартах нет людей).

**NOTE:** PR-C команда вызывается ВРУЧНУЮ, не через `landing-orchestrator`. Интеграция — задача PR-D.

См. [spec](docs/superpowers/specs/2026-05-13-visual-generation-design.md) и [plan](docs/superpowers/plans/2026-05-13-visual-generation-plan.md).

## Новая команда PR-D (Orchestrator Integration)

- `/landing-go` — **главная** команда: single entry point. Читает `.landing-state.yaml`, диспатчит следующий этап через `landing-orchestrator`.

**Workflow PR-D (prototype-first):**
1. Положи `prototype.pdf` в `<project>/07_ПРОТОТИП/source/`.
2. Запусти `/landing-go`.
3. Следуй подсказкам — оркестратор сам ведёт через все этапы:
   - 07a prototype parse (авто)
   - 03 references → 04 brand → 05 design (user-interactive)
   - 06 stack → 07 content (авто)
   - 07b wireframe (user picks variants) → 07c composed (авто)
   - **07d photos ⇆ 07e visuals параллельно**
   - 07f composed final → 08 build → 09 deploy → 10-12

**Auto-fix:** при падении гейта оркестратор предлагает фикс и применяет на `yes`.

**Этапы 00/01/01a/02 помечены `n/a`** — они происходят до landing-system (prototype-first).

**Установка codex CLI:** `bash scripts/install-codex.sh` (в onboarding).

**Lucide icons:** простые иконки берутся бесплатно из Lucide вместо codex API.

**Migration:** для существующих проектов — `bash scripts/migrate-state-for-prd.sh <project>/.landing-state.yaml`.

См. [spec](docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md), [plan](docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md).

## Block Library

Общая библиотека wireframe-блоков: `block-library/`. См. `block-library/README.md`.

## Атрибуция

См. `THIRD_PARTY_NOTICES.md` — мы используем фрагменты OpenDesign (Apache-2.0).

## Зависимости

Эта система использует:
- **superpowers** plugin (brainstorming, writing-plans, executing-plans, subagent-driven-development)
- Скиллы из `skills/` (landing-project-init, landing-from-context)
- Агентов из `agents/` (landing-orchestrator)

Перед работой проверь: `scripts/check-deps.sh`.

## Структура

- `template/` — каноничный шаблон проекта-лендинга (13 папок 00–12)
- `skills/` — наши специализированные скиллы
- `agents/` — специализированные агенты
- `.claude/commands/` — slash-команды
- `docs/superpowers/` — спецификации и планы реализации

## Правила работы

1. **TDD строго:** каждое изменение в коде начинается с failing test (через `bats` для bash, `vitest` для JS, `pytest` для Python).
2. **YAGNI:** не реализуем то, чего нет в spec.
3. **Frequent commits:** один commit = одна логическая единица.
4. **HARD GATE между этапами проектов:** агент не идёт на следующий этап workflow без явного утверждения пользователем.

## Для нового проекта-лендинга

При запуске `/landing-new my-project` агенты:
1. Создают `~/Lendings/my-project/` со структурой template/.
2. Запускают `landing-orchestrator`, который ведёт через 12 этапов.
3. На каждом этапе генерируют HTML-preview, ждут подтверждения.
4. Финал — деплой на Бегет, готовый сайт.

## Поддержка

Spec-документ: [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](docs/superpowers/specs/2026-05-03-landing-system-design.md)
Master plan: [`docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)

## Workflow Lock (новое)

С 2026-05-04 система использует принудительный workflow:

- Перед `/landing-*` командой нужен пройденный onboarding (`~/.landing-system/setup_complete`)
- Каждый проект имеет `.landing-state.yaml`, фиксирующий статус 13 этапов
- `scripts/gate-check.sh` проверяет каждый этап (hard+soft checks)
- `landing-orchestrator` НЕ пропускает этапы, даже если пользователь просит

Подробнее: [`docs/SETUP.md`](docs/SETUP.md), [`docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md`](docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md)
