# Landing System — CLAUDE Instructions

Это папка мастер-системы для производства WordPress-лендингов через Claude Code.

## Что это

Агентская система для построения production-grade лендингов на WordPress + Бегет.
Полный цикл: бриф → мудборд → бренд-кит → DESIGN.md → код → деплой → QA → SEO.

## Главные команды

- `/landing-start` — **главная команда для новичков**. Interactive wizard: объясняет систему, создаёт папку, проводит через 4 шага материалов (PR-E)
- `/landing-new <slug>` — advanced: создать пустой проект без wizard (для опытных)
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

## Новая команда PR-E (Onboarding Wizard)

- `/landing-start` — **главная точка входа** для нового проекта. Interactive wizard.

**Что делает:**
1. Welcome (3 параграфа объяснения системы)
2. Спрашивает имя проекта (kebab-case)
3. Создаёт `~/Lendings/<slug>/` с 18 подпапками и READMEs внутри
4. Проводит через 4 шага материалов:
   - 🔴 **Прототип** (обязательно) → `07_ПРОТОТИП/source/`
   - 🟡 **Фото клиента** (рекомендую) → `07c_PHOTOS/inbox/`
   - 🟡 **Логотип** (рекомендую) → `04_БРЕНД/logos/`
   - ⚪ **Референсы** (опционально) → `03_РЕФЕРЕНСЫ/`
5. Проверяет наличие материалов после каждого шага
6. Финиш — подсказка `/landing-go`

**Migration для старых проектов:**
```bash
bash scripts/migrate-template-readmes.sh ~/Lendings/<existing-project>
```
Добавит недостающие READMEs во все папки + создаст `04_БРЕНД/logos/` если её нет.

См. [spec](docs/superpowers/specs/2026-05-14-pr-e-onboarding-wizard-design.md), [plan](docs/superpowers/plans/2026-05-14-pr-e-onboarding-wizard-plan.md).

## Quality Standards (обязательные)

Каноничные стандарты качества для каждого этапа лежат в `docs/standards/`.
Они переопределяют любые «по умолчанию» решения агентов.

| Этап | Стандарт | Verify-скрипт |
|---|---|---|
| 07b Compose | [`docs/standards/premium-07b-checklist.md`](docs/standards/premium-07b-checklist.md) | `scripts/verify-composed-premium.sh` |

**Правило:** HARD GATE 07b не закрывается, пока `verify-composed-premium.sh`
не вернёт exit 0. Если фичи отсутствуют — `block-composer` обязан доработать
composed.html, а не предлагать «и так сойдёт».

Эталон-референс — `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html`
(1757 строк, все 13 premium-фич, реальные фото).

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
- `scripts/wiki/` — wiki-компайлер (3 режима: system / project-graph / conversations). См. `scripts/wiki/README.md`.
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

## Wiki Auto-Sync (правило)

С 2026-05-15 системная wiki (`landing-system/wiki/`) **обязана быть синхронной с исходниками** в каждом коммите.

**Источники wiki:**
- `agents/*.md`                         — агенты pipeline
- `skills/*/SKILL.md`                   — описания скиллов
- `commands/*.md`                       — слеш-команды
- `template/*/README.md`                — этапы шаблона
- `docs/standards/*.md`                 — правила (premium checklist)
- `block-library/*/*/meta.yaml`         — все блоки (200+)
- `block-library/_patterns/*/meta.yaml` — премиум-эффекты (PR-S)
- `block-library/_styles/*/README.md`   — style moods (PR-S)
- `config/*.yaml`                       — stage-gates и др. конфиги (PR-S)
- `docs/SETUP.md`                       — главная инструкция (PR-S)
- `docs/superpowers/specs/*.md`         — спецификации PR'ов (PR-T)
- `docs/superpowers/plans/*.md`         — планы реализации (PR-T)
- `docs/ПЛАН-ДОРАБОТОК.md`, `docs/BACKLOG.md`, `docs/photo-selection-guide.md` — главные планы и гайды (PR-T)
- `docs/superpowers/DOKRUTKA-system.md` — общий план доработок (PR-T)
- `tests/*/README.md`                   — описания тест-групп (PR-T)
- `presets/*.{md,yaml}`                 — пресеты (PR-T)
- `scripts/**/*.doc.md`                 — авто-сгенерированные доки скриптов из docstring/header (PR-T, см. `scripts/generate-script-docs.py`)

**Авто-механика (PR-G):**
- `.githooks/post-commit` запускается после каждого `git commit`.
- Если коммит трогает любой из источников выше → `compile.py --source-mode=system`.
- Хэш-кэш скипает неизменённое (~0 сек если ничего не менялось).
- Если wiki/ обновилась → авто-`chore(wiki)` коммит без `--verify`.

**Установка хука на новой машине:**
```bash
bash scripts/install-git-hooks.sh
```

**Проверить что wiki в синхроне:**
```bash
bash scripts/check-wiki-sync.sh
# exit 0 — синхрон, exit 1 — нужно пересобрать
```

**Если правило нарушено:**
- Хук не установлен → `bash scripts/install-git-hooks.sh`
- Wiki разошлась с источниками → `python3 -m scripts.wiki.compile --source-mode=system && git add wiki/ && git commit -m "chore(wiki): manual resync"`

**Никогда не коммить изменения в `agents/`, `skills/`, `commands/`, `template/`, `docs/standards/` без свежей wiki.** Хук это делает автоматом, но если хук отключён или упал — пересобирай руками.

## Multisite режим и сегменты ЦА (S2-CD CD1)

С 2026-05-18 landing-system поддерживает multisite-режим: один клиентский
корневой домен (`liauto.dubai`) может содержать N сегментов целевой
аудитории (`russian.liauto.dubai`, `family.liauto.dubai`, ...),
каждый — отдельный WordPress subsite в одной multisite-сети.

### Команды

- `/landing-segment <slug>` — создать новый сегмент ЦА (subdomain + WP subsite).
  При первом сегменте автоматически мигрирует проект single-site → multisite.
- `/landing-clone <source> <dest>` — byte-by-byte копия сегмента в новый сегмент.

### Артефакты

- `.landing-state.yaml::multisite` (bool) — флаг режима.
- `.landing-state.yaml::audience_segments[]` — список сегментов с blog_id и host.
- `13_СЕГМЕНТЫ_ЦА/<slug>/subbrief.yaml` — бриф сегмента (заполняет маркетолог).
- `13_СЕГМЕНТЫ_ЦА/<slug>/.subsite-meta.yaml` — машинные метаданные.

### Скилл

`skills/wp-multisite/` — содержит migrate-to-multisite, landing-segment,
clone-subsite + lib (beget-api, ssh-helpers, state).

### Required .env

Помимо стандартных BEGET_*, для multisite требуется `BEGET_SITE_ID`
(integer id «site-entity» на Бегете — получить через
`beget_api site/getList` для соответствующего public_html).

См. также [docs/beget-cookbook.md](docs/beget-cookbook.md),
[docs/superpowers/specs/2026-05-18-s2cd-multisite-cloning-design.md](docs/superpowers/specs/2026-05-18-s2cd-multisite-cloning-design.md).

## Landing-config mu-plugin (S2-A)

С 2026-05-19 landing-system включает pre-built mu-plugin `landing-config`
который даёт клиенту и маркетологу через wp-admin настраивать:
- CRM/мессенджеры (6 адаптеров: Email, Telegram, WhatsApp, AmoCRM, Bitrix24, HubSpot)
- CTA-кнопки (5 пресетов с per-site override)
- Head & SEO (GA4, Y.Metrika, FB Pixel, GSC, OG, custom HTML)
- Заявки (per-blog таблицы wp_<bid>_landing_leads + admin UI)

Multisite-aware: network defaults + per-site override; per-blog таблицы заявок.

### Установка на проект

```
/landing-admin-install
```

### REST endpoint для форм

```
POST /wp-json/landing/v1/lead
Body: name=... phone=... email=... message=... source_block=... utm_source=...
```

Защита: honeypot-поле `website` (должно быть пустым), rate-limit 10 req/hour per IP.

### Helper-функции для тем

```php
landing_get_cta('primary', $url_override = null, ['model' => 'X']);
landing_render_head_extras();  // вызывается автоматически на wp_head
landing_config_get('key', $default);
```

### Spec

[docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md](docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md)
