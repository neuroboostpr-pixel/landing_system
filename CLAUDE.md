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

## Reference-Driven Flow (2026-06-12) — главный флоу производства

Система переведена с «блочного» способа (подбор из библиотеки + wireframe) на
**reference-driven**: агент РИСУЕТ макет composed.html сам по двум материалам клиента —
**прототипу** (правда о структуре, 1:1) и **референсу-скриншоту** (правда о виде).
Канон: [`docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md`](docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md).

**Правило трёх источников (нарушение = дефект):**
- **Вид** (цвета, шрифты, кнопки, характер) — из референса клиента (скриншот, палитра по пикселям)
- **Структура** (какие блоки, порядок, тексты, кнопки) — из прототипа 1:1, ничего не выдумывать
- **Красота/глубина** (блобы, слои, вырезанные фото, крупные цифры) — из правил коллажа (спека §3)

Раскладку у референса НЕ брать (если клиент явно не указал). Элементы, которых
нет в прототипе, НЕ выдумывать.

**Команды этапа 07:**
- `/landing-prototype` — импорт прототипа (DOCX/PDF/MD) → prototype.{md,yaml}. **B37: точность парсинга** — для .docx работает детерминированный `extract-docx-text.py` (весь текст + таблицы с ценами), а hard-gate 07a `prototype_fidelity` не даёт закрыть этап при потере >10% текста или выдуманной структуре. Комментарии клиента → секция `client_notes`. Канон: [`docs/standards/prototype-fidelity.md`](docs/standards/prototype-fidelity.md).
- `/landing-content` — извлечение РЕАЛЬНЫХ текстов из prototype.yaml → content.md (БЕЗ Lorem ipsum)
- `/landing-compose` — composed.html: агент рисует макет с tokens + текстами прототипа, placeholders для визуала

## Style Moods = переключатель палитры (PR-S, пересмотрено 2026-06-12)

6 цветовых наборов в `block-library/_styles/` (brutalist, editorial-warm,
swiss-modernist, retro-windows, coral-soft, monochrome-precision) работают как
**переключатель палитры уровня темы/сайта**: дизайн-система проекта берётся из
референса клиента, а готовые наборы — альтернативные палитры на примерку
(плагин `lp-preview-panel`, спека §2.5). Переключение меняет ТОЛЬКО цвета — и
работает только при 100% токенизации (ни одного прямого цвета вне `:root`).

Mood-табы wireframe (старый PR-S UI) удалены вместе с wireframe-этапом.
Руководство по выбору mood: [`docs/MOOD-SELECTION-GUIDE.md`](docs/MOOD-SELECTION-GUIDE.md).

## Новые команды PR-B (Photo Pipeline)

- `/landing-photos` — обработка клиентских фоток: AI-classify через codex, matching к слотам, generative fallback для пустых слотов. **Stage 07c.**

**Workflow PR-B:**
1. Утверди этапы 05 (design-system) и 07a (prototype).
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
   - 07c composed (агент рисует макет по прототипу + референсу)
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

| Стандарт | Применяется | Verify-скрипт |
|---|---|---|
| [`stage-execution-protocol.md`](docs/standards/stage-execution-protocol.md) | **Все этапы** — обязательный протокол для orchestrator и любых stage-агентов | `scripts/render-pipeline-map.sh` (показывает карту) |
| [`reference-driven-rules.md`](docs/standards/reference-driven-rules.md) | 07c Compose — правило трёх источников, поблочная сверка, composed=канон | гейт `structure_check_md` + `verify-content-preserved.sh` |
| [`design-elements-rules.md`](docs/standards/design-elements-rules.md) | 07c Compose — декор/иконки/разделители, дерево решений | — |
| [`premium-07b-checklist.md`](docs/standards/premium-07b-checklist.md) (v2) | 07c Compose | `scripts/verify-composed-premium.sh` |
| Токенизация цветов (спека §4.3) | 07c + 08 | `scripts/verify_tokens.py` |
| Болячки сборки (спека §4.2) | 08 Build | `skills/wp-gutenberg-block-builder/scripts/lint-theme-php.py` |
| [`logo-icon-favicon.md`](docs/standards/logo-icon-favicon.md) | 07d/08/09 — логотипы, favicon | — |
| [`image-pipeline.md`](docs/standards/image-pipeline.md) | 07d/07e — генерация картинок | — |
| [`asset-pipeline.md`](docs/asset-pipeline.md) | 08 Build — фото, SVG, фавиконы, логотипы, CSS-фоны | `pytest tests/phase-stage-08/test-fix-page-content-images.py` |
| [`stage-08-spec-lint.md`](docs/standards/stage-08-spec-lint.md) | 08 Build — composed↔spec соответствие | `python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py --project <p>` |

**Stage Execution Protocol (главное правило):**
Перед ЛЮБЫМ действием на этапе агент обязан: (1) прочитать `.landing-state.yaml` и показать Mermaid-карту через `render-pipeline-map.sh`, (2) выписать все оставшиеся этапы в TodoWrite, (3) подгрузить `stage-<id>-checklist.md` если есть и создать под-todo, (4) verify → approve. Не пропускать шаги, даже если пользователь торопит.

**Правило 07b:** HARD GATE 07b не закрывается, пока `verify-composed-premium.sh` не вернёт exit 0. Если фичи отсутствуют — `block-composer` обязан доработать composed.html, а не предлагать «и так сойдёт».

Эталон-референс — `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html`
(1757 строк, реальные фото). Обязательный минимум — premium-чеклист v2
(verify-composed-premium.sh): токены/clamp/движение/головa документа/без эмодзи;
интерактивные фичи — под потребность места (design-elements-rules.md).

## Asset Pipeline (Stage-08)

Любой ассет лендинга — фото, иконка (inline SVG или файловая), фон,
фавикон, логотип — проходит через единый контракт, описанный в
[`docs/asset-pipeline.md`](docs/asset-pipeline.md).

**Правила в одну строку:**
- Фото и raster-иконки → `wp media import` → `{id,url}` URL-encoded JSON-строкой
  в page-content (`IMAGE_ATTR_KEYS`).
- Inline SVG → raw `<svg>` URL-encoded строкой в textarea-attr
  (`SVG_ATTR_KEYS`); block.php рендерит через `wp_kses(rawurldecode(...), $svg_allowed)`.
- CSS-фоны → НЕ через page-content, а в `assets/css/main.css` через
  `url('../photos/X.jpg')`.
- Фавикон / site icon → site-level через `wp_options`, не атрибут блока.

Любые изменения трансформации — только в
[`skills/wp-cli-deployer/scripts/fix-page-content-images.py`](skills/wp-cli-deployer/scripts/fix-page-content-images.py)
+ тест в `tests/phase-stage-08/test-fix-page-content-images.py`. Двойной
источник правды — баг.

## Архив блочного трека (reference-driven flow, 2026-06-12)

Библиотека готовых блоков и wireframe-этап выведены из эксплуатации и лежат в
`archive/` (история сохранена через git mv). Новый флоу: агент **рисует** макет
composed.html сам по прототипу и референсу клиента — канон:
[`docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md`](docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md).

Переиспользуемое (НЕ удалять): `block-library/_styles/` (палитры-moods),
`_shapes/` (подсказка для генерации декора), `_patterns/`, `_assets/`,
slot-формат `{{slot:name}}`, Lazy Blocks, плагин lp-preview-panel.

Slot-формат `{{slot:name}}` остаётся обязательным для редактируемого контента
в макете (основа slot→поле в Lazy Blocks, спека §4.5).

Guard: `pytest tests/archive/` не даёт живому коду ссылаться на архив.

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

## Wiki Routing Observability (правило)

Каждый агент (`agents/*.md`) и скил (`skills/*/SKILL.md`) **обязан** содержать в pre-flight блоке строку логирования:

```bash
# Агент:
python -m scripts.wiki.log --type agent_call --agent <slug> --stage <N>

# Скил:
python -m scripts.wiki.log --type skill_call --skill <slug> --stage <N>
```

**Правила:**
1. **При создании** нового агента/скила — строка логирования обязательна. Шаблон: `docs/standards/stage-agent-preamble.md` (шаг 6).
2. **При переименовании** агента/скила (`mv agents/old.md agents/new.md`) — обновить `--agent old` → `--agent new` в той же строке внутри файла.
3. **`<slug>`** = имя файла без `.md` (для агентов) или имя папки (для скилов).
4. **`<N>`** = числовой номер этапа к которому привязан агент/скил (например `04`). Если не привязан к конкретному — передать `""`.

Нарушение этих правил приводит к появлению ложных ⚠️ утечек в `wiki/routing-report.md`.

## Wiki Auto-Sync (правило)

С 2026-05-15 системная wiki (`landing-system/wiki/`) **обязана быть синхронной с исходниками** в каждом коммите.

**Источники wiki:**
- `agents/*.md`                         — агенты pipeline
- `skills/*/SKILL.md`                   — описания скиллов
- `commands/*.md`                       — слеш-команды
- `template/*/README.md`                — этапы шаблона
- `docs/standards/*.md`                 — правила (premium checklist)
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
- Снипеты (произвольный HTML в head/body_open/footer; network-level + per-site override через `name`)
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

### S2-A.3 — Network-Admin Unification (2026-05-20)

Все настройки (CTA / Интеграции / Снипеты) теперь в **Network admin → Лендинг**
с селектором сегмента `?segment=N` (0 = network default, N = blog_id сегмента).
Cascade: network запись → site override по machine-id
(preset_name / adapter_name / snippet name).

- 3 CPT: `lp_cta`, `lp_integration`, `lp_snippet`
- Общий резолвер: `includes/cascade.php` (resolve_for_blog / list_for_blog / has_site_override)
- Сегмент-селектор: `includes/segment-selector.php` (render + current_from_request)
- Network admin pages: `admin-cta.php`, `admin-integrations.php`, `admin-snippets.php`
  (последний — merged из бывшего `admin-snippets-network.php`)
- Read-only view на subsite: `admin-cta-readonly.php`, `admin-integrations-readonly.php`,
  `admin-snippets-readonly.php`
- Миграция wp_options → CPT (идемпотентно, один раз):
  - `migrate_cta_from_options`
  - `migrate_integrations_from_options` (per-network)
  - `migrate_subsite_integrations` (per-subsite, для каждого blog_id)
  - Маркер `landing_config_migration_s2a3_cta` ставится в `maybe_run()` после
    ВСЕХ миграций (не из отдельных миграционных функций).
- Адаптеры расширены: `field_definitions()` (декларативная схема с encrypt/required)
  + `settings()` (cascade-aware reader с legacy fallback на per-field wp_options).
- Live smoke: `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh`

См. [spec](docs/superpowers/specs/2026-05-19-s2a3-network-admin-unification-design.md)
и [plan](docs/superpowers/plans/2026-05-19-s2a3-network-admin-unification-plan.md).

### S2-A.4 — Lead Status Workflow MVP (B19, 2026-05-20)

Маркетолог управляет статусами заявок через wp-admin:

- 4-я ось cascade S2-A.3: CPT `lp_lead_status` (slug/label/color/order) с network→site override
- Network admin → Статусы заявок: редактирование словаря с селектором сегмента
  (slug `landing-config-network-lead-statuses`, cap `manage_network_options`)
- На subsite: `Лендинг → Статусы заявок` — read-only список с deep-link на network editor
  (slug `landing-config-lead-statuses`, cap `manage_options`)
- Карточка заявки: клик по имени в списке → детальная страница с timeline истории
  и модальным окном смены статуса (select + textarea для комментария)
  (slug `landing-config-lead-detail?id=N`, скрытая)
- Список заявок (`landing-config-leads`) расширен: subsubsub-табы по статусу со
  счётчиками, колонка «Статус» с цветным бейджем (warning-style если slug
  не в vocab), checkbox-колонка, bulk-action «Изменить статус» с modal-like
  страницей-формой
- Per-blog таблица `wp_<bid>_landing_lead_status_log` (lead_id/user_id/from/to/
  comment/created_at) — полная история изменений
- Транзакции на смену статуса: log_status_change + UPDATE landing_leads атомарны;
  bulk-action использует per-lead транзакции — ошибка одной не блокирует остальные
- Whitelist валидация to_status в двух местах: handler и `log_status_change`
  (defense-in-depth)
- Lessons из transaction safety: `wp_die` ВНЕ try-catch через флаг (избегаем
  double-ROLLBACK при WP_Die_Exception); `$wpdb->update` проверяется `=== false`
  → throw RuntimeException → catch ROLLBACK
- Seed 5 default-статусов (pending/in_progress/won/lost/spam) в `maybe_run()`.
  Идемпотентно — если хоть один статус есть, не трогает. На уже-мигрированных
  сайтах с выставленным marker — ручной вызов:
  ```bash
  wp eval 'LandingConfig\\Migrate\\seed_default_lead_statuses(1);'
  ```
- Live smoke расширен T7/T8 (CPT count + lead-detail URL)

CRM sync (двусторонняя — webhook из CRM в админку и push из админки в CRM)
явно вне scope MVP. Требует расширения AdapterInterface::update_status() и
тестов с реальными credentials всех 5 адаптеров (B20).

См. [spec](docs/superpowers/specs/2026-05-20-b19-lead-status-workflow-design.md)
и [plan](docs/superpowers/plans/2026-05-20-b19-lead-status-workflow-plan.md).

### B1 — Cookie-banner + 152-ФЗ согласие на ПД (2026-05-21)

Template-level юр-инфраструктура для каждого лендинга:

- **brand-kit.md ## Legal секция** — реквизиты Оператора ПД (company_name, entity_type,
  inn, ogrn, legal_address, contact_email, dpo_email). Собирается brand-architect'ом
  на этапе 04, парсится через `skills/brand-kit-build/scripts/parse_legal.py`.
- **Cookie-banner с категориями** (`template/08_КОД/template-parts/cookie-banner.{php,js,css}`)
  — Necessary (locked) / Analytics / Marketing. localStorage `lp_cookie_consent`
  с версионированием. Появляется при первом визите, footer-кнопка для
  переоткрытия.
- **Google Consent Mode v2** (`consent-init.php`) — gtag('consent','default','denied')
  в <head> ДО загрузки Metrica/GTM/GA4. После save в баннере — consent.update.
- **Legal-block в формах** (`legal-block.php`) — обязательный checkbox согласия
  на ПД с required-валидацией. Не pre-checked (152-ФЗ ст.9 — явное согласие).
- **Бэкенд-валидация** в REST /wp-json/landing/v1/lead — 400 если pd_consent != '1',
  при успехе пишет timestamp `pd_consent_granted_at` в landing_leads (формальное
  доказательство согласия для возможных проверок Роскомнадзора).
- **Юр-страницы** (`template/08_КОД/legal-pages/{policy,consent}.html.template`) —
  типовые тексты с {{placeholders}} для подстановки реквизитов из brand-kit.
  Создаются через `skills/wp-builder/scripts/install_legal_pages.sh` (wp-cli upsert
  по meta `_lp_legal_page`).
- **Stage-gate soft-check** `legal_blocks_present` — grep по wp-theme что
  cookie-banner/consent-init/legal-block подключены в footer/header/блоках форм.

ВАЖНО: тексты policy/consent — типовые, основаны на формулировках Роскомнадзора.
Перед прод-деплоем у клиента — обязательная проверка юристом.

См. [spec](docs/superpowers/specs/2026-05-21-b1-cookie-banner-pd-consent-design.md)
и [plan](docs/superpowers/plans/2026-05-21-b1-cookie-banner-pd-consent-plan.md).

### B2 — Cookie-banner Library (5 layouts + admin, 2026-05-22)

Replaces B1's hardcoded cookie-banner with a mu-plugin-owned library:

- **5 layouts:** top-bar / bottom-bar / floating-card-{left,right} / center-modal.
  Маркетолог выбирает radio-button'ами с preview-thumbnail'ами в Network admin.
- **Admin UI:** Network admin → Лендинг → Cookie-banner с селектором сегмента
  (network default + per-segment override через cascade S2-A.3 паттерн).
  Поля: layout, тексты (заголовок/описание/кнопки/policy-link/reopen),
  категории (repeater с slug/name/desc/locked/default_on), цвета (4 hex
  поля — bg/text/accent/border, пусто = inherit из brand-kit темы),
  consent version (bump → re-prompt всем).
- **Token-driven design:** banner-local CSS-vars (`--cb-bg`, `--cb-accent`,
  `--cb-text`, `--cb-border`) по умолчанию ссылаются на theme vars
  (`var(--color-bg-card, ...)` etc). Admin-override эмитится inline `<style>`
  с более высоким specificity.
- **Google Consent Mode v2:** `gtag('consent','default','denied')` в `wp_head`
  с priority 1 (до загрузки analytics). После save в banner →
  `gtag('consent','update', {...})` per-category через GTAG_MAP.
- **B1 deprecation:** файлы `template/08_КОД/template-parts/cookie-banner.*` +
  `consent-init.php` удалены — mu-plugin полностью владеет рендером. Это
  решает баг «functions.php регенерируется без B1-хуков».
- **Migration:** `landing_config_migration_b2_cookie_banner` marker seed'ит
  network default запись с 3 категориями (necessary/analytics/marketing) при
  первой загрузке wp-admin.

См. [spec](docs/superpowers/specs/2026-05-22-b2-cookie-banner-library-design.md)
и [plan](docs/superpowers/plans/2026-05-22-b2-cookie-banner-library-plan.md).

### S2-E.1 — SEO/Tech Audit Skill (2026-05-22)

Skill `seo-tech-audit` + slash-команда `/landing-audit` запускают аудит задеплоенного лендинга — 43 HTTP-проверки (HTML on-page, network/infra, schema). Multisite-aware: auto-discovery поддоменов из `.landing-state.yaml::audience_segments`.

**Что проверяется (E1):**
- HTML (25): title/meta/h1/canonical/lang/img-alt/anchor-noopener
- Network (13): SSL валиден ≥7 дней, www→non-www 301, robots.txt + sitemap.xml + ссылка из robots, 404 не soft-200, security headers ≥3/4, Whois (info)
- Schema (5): Open Graph 5 свойств, Twitter Card, JSON-LD парсится, favicon

**Что НЕ в E1 (отдельные итерации):**
- Lighthouse Web Vitals (LCP/CLS/INP) — E2
- Crawler битых ссылок — E2
- Content metrics RU (тошнота/Flesch/водность) — E3
- AI readiness (llms.txt extended) + auto-fix loop в orchestrator — E4

**Использование:**
```bash
/landing-audit dubai-avto-liza             # все поддомены проекта
/landing-audit https://example.com         # ad-hoc URL
/landing-audit dubai-avto-liza --site russian.ailexi.ru
```

**Output:**
```
<project>/11_QA/
├── audit-report.md       # сводный (все поддомены, таблица)
├── audit-report.json     # машино-читаемый
└── per-site/
    └── <host>.{md,json}
```

**Stage-11 gate:** `seo_audit_pass` в `config/stage-gates.yaml`. Stage-11 не закрывается пока hard-gate fails на любом поддомене.

**Pure Python:** без зависимости от Lighthouse/Node (`requests`+`beautifulsoup4`+`lxml`+`python-whois`).

См. [spec §13](docs/superpowers/specs/2026-05-15-s2e-seo-tech-audit-design.md) и [plan E1](docs/superpowers/plans/2026-05-22-s2e-e1-seo-audit-skill-plan.md).

### S2-E.4 — Audit Dashboard + Head & SEO Settings (2026-05-22)

Network admin интерфейс для запуска audit и редактирования SEO-параметров:

- **Меню `Лендинг → Аудит`** с табами Обзор / HTML / Network / Schema / AI readiness.
  Селектор сегмента (all/0/N) переключает между multisite-aggregate, network default
  и конкретными subsites. Кнопка «Запустить» — shell_exec в Python skill `seo-tech-audit`.
- **Меню `Лендинг → Head & SEO`** — settings page (description, OG image picker,
  OG type, Twitter card, llms.txt content) с **live preview** OG-карточки
  (стиль Facebook/Telegram) и SERP-сниппета (стиль Google).
- **Cascade** для head-seo settings (network default + per-site override) — тот же
  паттерн что Cookie-banner (`switch_to_blog(NETWORK_BLOG_ID)`).
- **Deep-links на failures** — каждый failed check в admin получает кнопку «Открыть»
  ведущую в нужное место WP admin (settings page / post editor / Customizer).
  Каталог fix-actions: 46 записей (43 + AI1/AI2/AI3), генерится Python'ом в JSON
  для PHP consumption.
- **AI readiness (3 проверки)** — `AI1` llms.txt валиден, `AI2` JSON-LD
  Organization/Product/FAQ, `AI3` body содержит ≥1KB текста без JS.
  Добавлено в Python skill `seo-tech-audit`.
- **CLI расширение:** `run-audit.py --hosts-file <file>` (multisite batch
  без `.landing-state.yaml`), `--with-fix-hints` (enrich failures с
  fix_action metadata).
- **llms.txt rewrite rule** — mu-plugin регистрирует `add_rewrite_rule` для `/llms.txt`,
  content берётся из option `landing_seo_llms_txt` (редактируется в Head & SEO admin).
  После деплоя нужен `wp rewrite flush` (или Settings → Permalinks → Save).
- **Out of scope (S2-E.4):** auto-fix кнопки (только deep-links), cron,
  history snapshots, page-level overrides.

См. [spec](docs/superpowers/specs/2026-05-22-s2e-e4-audit-dashboard-design.md)
и [plan](docs/superpowers/plans/2026-05-22-s2e-e4-audit-dashboard-plan.md).
