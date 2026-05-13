# Handoff: проектирование frontend-builder agent

**Дата:** 2026-05-13
**Статус:** Brief для нового чата. Brainstorming не закончен — будет проведён в новой сессии.

---

## Контекст: что уже сделано

Миграция stage-08 на **Lazy Blocks** завершена и смержена в `main` (HEAD `ecac86f`, 31 коммит, ветка `feat/stage08-lazy-blocks` удалена). Полный список изменений — в [`2026-05-13-stage08-lazy-blocks-migration.md`](../plans/2026-05-13-stage08-lazy-blocks-migration.md) (план миграции) и closing-note в [`2026-05-12-acf-block-rendering-research-NEEDED.md`](2026-05-12-acf-block-rendering-research-NEEDED.md).

Краткая суть текущего состояния:

- `08_КОД/block-spec.yaml` — single source of truth для **контента блоков**: list of blocks, controls per block, `css_class`/`element`/`wrapper_open_html`/`wrapper_close_html`/`href_from` поля. Manager-authored.
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — single source of truth для **CSS токенов**: `:root{}` блоки в §2 (colors/typography/spacing/radius/shadow/zIndex/motion) и `:root`-блоки + правила в §3-§9.
- Pipeline `scripts/generate-wp-blocks.py` (5 шагов):
  1. `generate-theme.py` — scaffold темы; `style.css` из DESIGN.md §2; `assets/css/main.css` из DESIGN.md §3-§9; `index.php` рабочий WP-template; `functions.php` базовый
  2. `generate-lzb-templates.py` — `wp-theme/blocks/lazyblock-<slug>/block.php` per block (skeleton)
  3. `generate-lzb-registration.py` — AUTO-GENERATED `lzb/init` секция в `functions.php`
  4. `generate-css-patches.py` — `display:contents` правила в `main.css` для InnerBlocks-обёрток
  5. `generate-page-content.py` — `08_КОД/page-content.html` (Gutenberg markup для seed front-page)
- `deploy-wordpress.sh` — ставит lazy-blocks plugin, импортит картинки в Media Library, seed'ит front-page через `wp post create`, выставляет `page_on_front`.
- Test-стенд `http://esper21.beget.tech/neuroupgrade-v2/` — 12 блоков зарегистрированы, контент в Gutenberg редактируется, фронт отвечает HTTP 200.

## Что не делается сейчас и почему это проблема

После полного pipeline на real-проекте neuroupgrade-v2 визуальный результат — **плоский поток текста**:
- `style.css` содержит дизайн-токены (`--bg-base: #0E2B30`, `--accent-coral: #E85E48` etc.) но не использует их
- `main.css` содержит только §3-§9 правила из DESIGN.md — там 3 fenced ```css блока (container, section padding, focus-visible), плюс §5 — **только описания** классов (`.hero__title`, `.pricing-card`) в буллет-списках, **без реальных rule-bodies**
- `block.php` шаблоны — generic skeleton без layout-awareness (Hero нуждается в 2-col grid copy+portrait на desktop / стек на mobile; Pricing — 3 карточки с popular middle; FAQ — `<details>` accordion; …)

То есть pipeline даёт **механику** (контент сохраняется, блоки регистрируются, $attributes доходят до PHP) но не **визуал**.

### Подходы которые я пробовала и почему провалились

1. **Generic CSS baseline в `generate-theme.py`** — я добавила generic стили (`.lp-block { padding: ... }`, `.nu-tier-grid { display: grid }`). Имена переменных не совпадали с DESIGN.md (я писала `--color-bg-base`, в DESIGN.md `--bg-base`). Конфликтовали с DESIGN-извлечёнными токенами. **Откатила** в commit `a8fffed` (refactor: DESIGN.md as SoT).

2. **Semantic heuristics в `generate-lzb-templates.py`** — по имени control'а решать какой HTML-элемент эмитить (`name==title`→`<h1>`, `name==eyebrow`→`<span>`, и т.п.). Получались плохо контролируемые догадки, неконсистентные классы. **Откатила** в commit `ecac86f` (drop heuristics).

3. **Spec-driven BEM-классы в block-spec.yaml** (текущее состояние) — добавила `css_class`/`element`/`wrapper_open_html`/`href_from` в block-spec, generator уважает. block.php теперь эмитит правильные BEM-классы (`hero__title`, `pricing-card--popular`). НО — этого недостаточно, потому что:
   - per-block layout (2-col hero grid, FAQ details, pricing badge) **не описывается** простым per-control wrapping
   - CSS-rules для этих классов **не написаны** нигде (DESIGN.md §5 — только описания)
   - manager не должен писать `wrapper_open_html` с PHP-кодом руками

## Что делать дальше: frontend-builder agent

### Цель

Новая стадия в `landing-build` flow **после** wp-builder. Frontend-builder читает:
- `08_КОД/block-spec.yaml` (skeleton с базовыми controls)
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` (wireframes §5, токены §2, layout primitives §3-§4, component states §9, motion §7, accessibility §8)
- `04_БРЕНД/brand-kit.md` (доп. контекст)
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` (контракт блоков)
- Уже сгенерированные `block.php` skeleton'ы (на которых построены controls)

И **переписывает**:
- Каждый `wp-theme/blocks/lazyblock-<slug>/block.php` — finalized layout-aware HTML (2-col grids, conditional classes, аккордеоны, accordions, etc.)
- Опционально: `wp-theme/assets/css/blocks.css` — реальный CSS для всех BEM-классов из DESIGN.md §5, основанный на per-block wireframes
- Опционально: `wp-theme/assets/js/<feature>.js` — minor JS (FAQ accordion toggle, mobile burger, sticky CTA observer)

### Граничные условия

- Не трогать `block-spec.yaml` (это manager-authored)
- Не трогать lzb/init registration (это pipeline отвечает)
- Не трогать page-content.html seed (pipeline)
- Может перезаписывать `block.php` (генератор шаблонов в pipeline и так оставляет существующие — но frontend-builder может проактивно перезаписывать после `--force` или просто принимать `block-spec.yaml` как input)
- Изменения в DESIGN.md делает дизайнер на stage-05, не frontend-builder

### Открытые архитектурные вопросы (для brainstorming в новом чате)

1. **agent vs skill vs subagent**: frontend-builder — это claude-agent (markdown в `agents/`), skill (scripts в `skills/`) или просто фаза в `landing-build` команде?
2. **Точка вызова**: после wp-builder в той же `/landing-build`? Отдельная команда `/landing-style`? Auto-trigger по gate?
3. **Что генерируется vs пишется LLM**: per-block CSS pattern — это шаблон с подстановкой (мог бы быть Python-script с template) или живой LLM-output по wireframe-ASCII из DESIGN.md §5? Hero layout уникален, его сложно "генерить" по правилам, проще попросить LLM сделать.
4. **Per-block CSS — в DESIGN.md §5 (как fenced блоки) или в отдельном `assets/css/blocks.css`**? Если в DESIGN.md — frontend-builder его и пишет, потом pipeline `design_extractor` подхватит. Если в отдельном — нужен новый шаг pipeline.
5. **Idempotency / regen**: что делать если manager отредактировал `block.php` руками после frontend-builder, потом запустил перегенерацию? `wp-gutenberg-block-builder` сейчас skip-if-exists — frontend-builder тоже?
6. **Mobile/responsive**: media queries для каждого блока — генерить LLM'ом или брать из DESIGN.md §3.3?
7. **Forms, motion, accessibility**: DESIGN.md описывает state machines (button hover, input focus, accordion open). Они общие — должны жить в base CSS темы, не per-block. Это в `assets/css/main.css` (через DESIGN.md §9) или новый `assets/css/components.css`?
8. **Stage gate**: после frontend-builder — manager approve визуально через browser? Какой gate-check?
9. **Test-стенд**: использовать ли existing `landing-qa` skill? Какие критерии "приёмки" frontend-builder вывода?

### Чек что зафиксировано в репо

- [`docs/superpowers/plans/2026-05-13-stage08-lazy-blocks-migration.md`](../plans/2026-05-13-stage08-lazy-blocks-migration.md) — план миграции (15 задач)
- [`docs/superpowers/specs/2026-05-13-block-spec-format.md`](2026-05-13-block-spec-format.md) — формат block-spec.yaml
- [`docs/superpowers/specs/2026-05-12-acf-block-rendering-research-NEEDED.md`](2026-05-12-acf-block-rendering-research-NEEDED.md) — research + closing note
- `skills/wp-gutenberg-block-builder/SKILL.md` — описание pipeline
- `skills/wp-cli-deployer/SKILL.md` — описание deploy
- `agents/wp-builder.md` — описание agent для stage-08
- `template/08_КОД/block-spec.example.yaml` — образец

### Test-проект для обкатки

`d:/AI_TEAMS/Lendings/neuroupgrade-v2/`:
- `04_БРЕНД/brand-kit.md` — полный (309 строк)
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — полный (1039 строк), 12 блоков с wireframes и описаниями классов
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — design-tokens.org формат (130 строк, реальные брендовые токены)
- `06_СТЕК/design-stack.yaml` — **stub** (создан временно для unblock pipeline; реальный `/landing-stack` не запускался). Это надо помнить.
- `07_КОНТЕНТ/final-copy.md` — 700+ строк финального контента
- `08_КОД/block-spec.yaml` — заполненный, 12 блоков с css_class/wrapper_html (от refactor'а sa-agent'а)
- `08_КОД/wp-theme/` — сгенерирован pipeline'ом, активен на сервере esper21.beget.tech

NeuroUpgrade — **обкатка flow**, не финальный продукт. Главное чтобы flow работал; визуальная точность под brand — критерий "passable", не "pixel-perfect".

## Конкретная задача для нового чата

> Контекст: см. этот документ. Миграция Lazy Blocks готова, pipeline даёт механику + skeleton. На реальном проекте neuroupgrade-v2 визуальная часть плоская — нет per-block layout и CSS-rules для классов из DESIGN.md §5.
>
> **Задача:** провести brainstorming + writing-plans для нового `frontend-builder` agent (или другой формы — обсудим), который превращает skeleton в визуально верную тему по DESIGN.md.
>
> Не начинай код. Сначала brainstorming → spec → план, потом исполнение в отдельной итерации.

### Состояние workspace на момент handoff

- HEAD `main`: `ecac86f`
- Worktree чистый: рабочий tree без uncommitted изменений (после этого коммита тоже)
- Test-стенд жив: HTTP 200, 18 Lazy Blocks зарегистрированы, page_on_front=83
