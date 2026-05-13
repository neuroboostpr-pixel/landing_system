# PR-D — Orchestrator Integration (Prototype-First Pipeline)

**Date:** 2026-05-13
**Status:** draft
**Scope:** PR-D из 4-частного апгрейда landing-system. Финальная сшивка PR-A + PR-B + PR-C + существующих 00-12 этапов в единый автоматизированный flow.

---

## Problem

После PR-A/B/C мы имеем 4 независимых конвейера, каждый со своей командой:
- `/landing-prototype` → `/landing-wireframe` → `/landing-compose` (PR-A)
- `/landing-photos` (PR-B)
- `/landing-visuals` (PR-C)
- `/landing-build` + `/landing-deploy` (существуют до PR-A)

Маркетолог должен помнить порядок, какие гейты должны быть утверждены, когда что запускать. Плюс:

1. `landing-orchestrator` знает только про 00-12 этапы, **не знает про PR-A/B/C** артефакты (07a/07b/07c/07d/07e/07f).
2. `wp-builder` (этап 08) читает `01a_АНАЛИЗ_НИШИ/landing-structure.md` — но в prototype-first flow мы 01a пропускаем (вход = готовый прототип).
3. `landing-photos` и `landing-visuals` запускаются последовательно вручную — могли бы идти параллельно.
4. При падении гейтов маркетолог сам разбирается что делать — нет автофиксов.
5. Простые иконки (menu, arrow, check) генерятся через codex API — дорого и медленно когда есть готовые Lucide SVG.
6. `landing-onboarding` объясняет старый flow без PR-A/B/C/D.
7. codex CLI не установлен автоматически — без него PR-B/C падают.

## Goals

1. **Одна команда `/landing-go`** — single entry point, читает state.yaml, диспатчит следующий этап.
2. **Prototype-first flow** — вход = `prototype.pdf` в `07_ПРОТОТИП/source/`. Этапы 00/01/01a/02 не требуются.
3. **Step-by-step UX** — на каждом этапе **одно действие маркетолога + одно ожидание + автогейт**.
4. **Авто-fix при падении гейта** — оркестратор предлагает фикс + применяет на approve.
5. **Параллельные этапы** — 07d_photos ⇆ 07e_visuals одновременно через `dispatching-parallel-agents`.
6. **Lucide для простых иконок** — экономия codex API + скорость.
7. **codex CLI install** — автопроверка в onboarding + guided install.
8. **Прежние команды сохраняются** — `/landing-photos` и т.д. остаются как ручные точки входа для повторных прогонов.
9. **Backward compatible с PR-A/B/C** — все артефакты, гейты, агенты работают как раньше.

## Non-goals (PR-D specific)

- ❌ Веб-интерфейс (отдельный PR-G позже)
- ❌ Улучшение качества вёрстки блоков (PR-F через OpenDesign skill-block-template)
- ❌ Усиление design-system-generator через 149 OpenDesign DESIGN.md (PR-E)
- ❌ A/B-тестирование
- ❌ Многоязычность
- ❌ Переписывание wp-builder/wp-deployer (используются как есть)
- ❌ SVG output для иконок (отложено, остаётся PNG)

## Decisions log

| # | Решение | Источник |
|---|---|---|
| D1 | Вход = только `prototype.pdf`. Этапы 00/01/01a/02 помечаются `n/a` в state.yaml. | "На этом этапе мы начинаем только с прототипа" |
| D2 | Design-system stage 05 использует существующий `design-system-generator` без изменений. | "По дизайну системы у нас уже есть готовый инструмент" |
| D3 | 03_references / 04_brand / 05_design / 07b_wireframe остаются интерактивными (маркетолог решает). | "дизайн система референсы бренд-кит это всё оставляем" |
| D4 | 07d_photos и 07e_visuals — параллельно через `superpowers:dispatching-parallel-agents`. | "параллельно можно делать" |
| D5 | Auto-fix: оркестратор парсит `fix_hint` из stage-gates.yaml, предлагает + применяет на «yes». | "автофикс ошибок он предлагает и делает" |
| D6 | Lucide branch добавляется как **первый** шаг в waterfall prompt-picker.py. Если matching icon в icons.csv с `Library=Lucide` → fetch SVG, конверт PNG, skip codex. | "подключим Ухпромакс или какие-то библиотеки" |
| D7 | Bridge скрипт `scripts/derive-landing-structure.py` генерит `01a_АНАЛИЗ_НИШИ/landing-structure.md` из `07_ПРОТОТИП/prototype.yaml` чтобы wp-builder работал. | wp-builder dependency analysis |
| D8 | `landing-onboarding` дополнен codex CLI install (`npm i -g @openai/codex`) + объяснение нового prototype-first flow. | "система онбординга нужно упростить" |
| D9 | Все gate failures записываются в `STATE.yaml:errors[]` с fix_hint. Auto-fix matching по error id. | Practical |
| D10 | Existing slash-команды (`/landing-prototype`, `/landing-photos`, `/landing-visuals`) сохраняются как direct entry points. `/landing-go` использует их под капотом. | Backward compat |

---

## Architecture

### State.yaml расширение

Добавить в `template/.landing-state.yaml`:

```yaml
stages:
  # Upstream (n/a в prototype-first flow, но track для совместимости)
  "00_brief":             {status: n/a, timestamp: ""}
  "01_context":           {status: n/a, timestamp: ""}
  "01a_niche_analysis":   {status: n/a, timestamp: ""}
  "02_assets":            {status: n/a, timestamp: ""}

  # User-interactive
  "03_references":        {status: locked, timestamp: ""}
  "04_brand":             {status: locked, timestamp: ""}
  "05_design":            {status: locked, timestamp: ""}

  # Auto
  "06_stack":             {status: locked, timestamp: ""}
  "07_content":           {status: locked, timestamp: ""}

  # NEW (PR-A artifacts now stage-tracked)
  "07a_prototype":        {status: in_progress, timestamp: ""}    # Entry stage
  "07b_wireframe":        {status: locked, timestamp: ""}
  "07c_composed":         {status: locked, timestamp: ""}

  # NEW (PR-B + PR-C, parallel)
  "07d_photos":           {status: locked, timestamp: ""}
  "07e_visuals":          {status: locked, timestamp: ""}

  # NEW (final re-render after photos+visuals)
  "07f_composed_final":   {status: locked, timestamp: ""}

  # Existing build/deploy/qa stages
  "08_build":             {status: locked, timestamp: ""}
  "09_deploy":            {status: locked, timestamp: ""}
  "10_qa":                {status: locked, timestamp: ""}
  "11_analytics":         {status: locked, timestamp: ""}
  "12_seo":               {status: locked, timestamp: ""}
```

**`n/a` статус:** новый status enum. gate-check.sh пропускает n/a stages при проверке `require_approved`.

### Stage gates для новых этапов

```yaml
"07a_prototype":
  require_approved: []  # entry stage
  hard_checks:
    - id: prototype_source_exists
      type: file_or_dir_exists
      path: "{project}/07_ПРОТОТИП/source"
      fix_hint: "Положи prototype.pdf или .md в 07_ПРОТОТИП/source/"
    - id: prototype_yaml_exists
      type: file_exists
      path: "{project}/07_ПРОТОТИП/prototype.yaml"
      fix_hint: "auto_fix: run prototype-importer"

"07b_wireframe":
  require_approved: ["07a_prototype"]
  hard_checks:
    - id: wireframe_html_exists
      type: file_exists
      path: "{project}/07a_WIREFRAME/wireframe.html"
      fix_hint: "auto_fix: run /landing-wireframe"
    - id: wireframe_selections
      type: file_exists
      path: "{project}/07a_WIREFRAME/selections.yaml"
      fix_hint: "Открой wireframe.html, выбери варианты блоков, нажми Confirm. Положи selections.yaml в 07a_WIREFRAME/"

"07c_composed":
  require_approved: ["07b_wireframe", "05_design"]
  hard_checks:
    - id: composed_html
      type: file_exists
      path: "{project}/07b_COMPOSED/composed.html"
      fix_hint: "auto_fix: run /landing-compose"

"07d_photos":
  require_approved: ["07c_composed"]
  hard_checks:
    - id: photo_selections_yaml
      type: file_exists
      path: "{project}/07c_PHOTOS/selections.yaml"
      fix_hint: "Открой 07c_PHOTOS/photo-board.html, расставь фото, скачай selections.yaml"

"07e_visuals":
  require_approved: ["07c_composed"]  # параллельно с 07d
  hard_checks:
    - id: visuals_generated
      type: dir_has_files
      path: "{project}/07d_VISUALS/icons"
      fix_hint: "auto_fix: run /landing-visuals"

"07f_composed_final":
  require_approved: ["07d_photos", "07e_visuals"]
  hard_checks:
    - id: composed_has_real_visuals
      type: script
      script: "scripts/verify-composed-has-visuals.sh"
      args: ["{project}/07b_COMPOSED/composed.html"]
      fix_hint: "auto_fix: re-run /landing-compose"
```

**Существующие checks для 08-09 дополняются:**

```yaml
"08_build":
  require_approved: ["07f_composed_final"]
  hard_checks:
    - id: wp_theme_exists
      type: dir_has_files
      path: "{project}/08_КОД/wp-theme"
    - id: theme_php_syntax_valid
      type: script
      script: "scripts/verify-php-syntax.sh"
      args: ["{project}/08_КОД/wp-theme"]
      fix_hint: "wp-builder сгенерил невалидный PHP — посмотри .logs/, re-run wp-builder"
    - id: gutenberg_blocks_valid
      type: script
      script: "scripts/verify-gutenberg-json.sh"
      args: ["{project}/08_КОД/gutenberg-blocks"]
      fix_hint: "Gutenberg block.json невалидный — посмотри errors"

"09_deploy":
  require_approved: ["08_build"]
  hard_checks:
    - id: site_url_accessible
      type: script
      script: "scripts/verify-site-url.sh"
      args: ["{project}/.landing-state.yaml"]
      fix_hint: "Сайт не открывается по URL. Проверь логи wp-deployer."
```

### Компоненты PR-D

| # | Файл | Действие | Ответственность |
|---|---|---|---|
| 1 | `commands/landing-go.md` | NEW | Single entry. Читает .landing-state.yaml, диспатчит current stage. Принимает `--auto-fix yes`, `--skip-gate <id>`. |
| 2 | `agents/landing-orchestrator.md` | UPDATE | Расширить dispatch table 21 этапом. Добавить prototype-first branch. Parallel dispatch для 07d+07e. Auto-fix mechanism. |
| 3 | `template/.landing-state.yaml` | UPDATE | Добавить 7 новых stages + `n/a` enum для 00-02. |
| 4 | `config/stage-gates.yaml` | UPDATE | Добавить hard/soft checks для 07a/07b/07c/07d/07e/07f + augment 08/09 проверками. |
| 5 | `scripts/gate-check.sh` | UPDATE | Поддержка status `n/a` (пропускать при require_approved). |
| 6 | `scripts/gate-state.sh` | UPDATE | Поддержка status `n/a` при transition. |
| 7 | `scripts/derive-landing-structure.py` | NEW | `07_ПРОТОТИП/prototype.yaml` → `01a_АНАЛИЗ_НИШИ/landing-structure.md` для wp-builder совместимости. |
| 8 | `scripts/verify-composed-has-visuals.sh` | NEW | Grep composed.html на `[SLOT:` или `[INFOGRAPHIC:` — если есть, fail. |
| 9 | `scripts/verify-php-syntax.sh` | NEW | `find <dir> -name "*.php" -exec php -l {} \;` |
| 10 | `scripts/verify-gutenberg-json.sh` | NEW | `find <dir> -name "block.json" → jq` |
| 11 | `scripts/verify-site-url.sh` | NEW | `curl -fsSI <url>` |
| 12 | `scripts/install-codex.sh` | NEW | npm check + install + `codex login` prompt |
| 13 | `skills/visual-generation/scripts/lucide-fetcher.py` | NEW | Download Lucide SVG by icon name, convert to PNG via Pillow/cairosvg. |
| 14 | `skills/visual-generation/scripts/prompt-picker.py` | UPDATE | Add Lucide as first step in icon waterfall. |
| 15 | `skills/landing-onboarding/SKILL.md` | UPDATE | Новый flow: codex install + «положи прототип → запусти /landing-go». |
| 16 | `agents/photo-curator.md` | UPDATE | Опциональный flag `--triggered-by orchestrator` (для отличия от ручного вызова). |
| 17 | `agents/visual-curator.md` | UPDATE | Same as above. |
| 18 | `tests/phase-prd/` | NEW | Тесты на all of the above. |
| 19 | `THIRD_PARTY_NOTICES.md` | UPDATE | Lucide attribution (ISC license). |
| 20 | `CLAUDE.md` | UPDATE | PR-D section: `/landing-go` workflow. |

### Поток `/landing-go`

```python
def landing_go(project_dir, auto_fix=False):
    state = load(project_dir / ".landing-state.yaml")
    next_stage = find_next_actionable_stage(state)

    if next_stage is None:
        print("✅ Все этапы завершены")
        return

    print(f"📋 Текущий этап: {next_stage}")
    instructions = STAGE_INSTRUCTIONS[next_stage]
    print(instructions.user_prompt)  # «Открой X, сделай Y, напиши 'готово'»

    wait_for_user_confirm()

    gate_result = run_gate_check(project_dir, next_stage)
    if not gate_result.passed:
        print(f"❌ Гейт {gate_result.failed_check_id} не прошёл")
        fix_hint = gate_result.fix_hint
        if fix_hint.startswith("auto_fix:"):
            action = fix_hint.removeprefix("auto_fix: ").strip()
            print(f"🔧 АВТОФИКС: запустить '{action}'? (yes/no)")
            if user_confirms() or auto_fix:
                run_fix_action(action)
                # re-run gate
        else:
            print(f"💡 Подсказка: {fix_hint}")
        return  # exit, user fixes, re-runs /landing-go

    mark_stage_approved(state, next_stage)
    save(state)

    # Special: 07c → dispatch 07d + 07e PARALLEL
    if next_stage == "07c_composed":
        print("⚡ Запускаю 07d_photos и 07e_visuals параллельно...")
        dispatch_parallel(
            [
                ("photo-curator", project_dir),
                ("visual-curator", project_dir),
            ]
        )

    print(f"✅ Этап {next_stage} утверждён. Запусти /landing-go снова для следующего.")
```

### Параллельная диспетчеризация (07d + 07e)

Оркестратор при достижении этапа 07d_photos/07e_visuals использует **superpowers:dispatching-parallel-agents** skill. Один сообщение с двумя Task tool calls:
- Subagent A: photo-curator → `07c_PHOTOS/`
- Subagent B: visual-curator → `07d_VISUALS/`

После обоих DONE → проверка обоих гейтов → переход к 07f.

### Lucide icon library integration

В `prompt-picker.py` waterfall становится 3 шага для иконок:

```python
def pick_icon_prompt(hint, brand_context, icons_csv, opendesign_index):
    # Step 1 (NEW): Lucide direct fetch — bypass codex entirely
    row = _icons_csv_match(hint, icons_csv)
    if row and row.get("Library") == "Lucide":
        svg_path = _fetch_lucide_svg(row["Icon Name"])
        if svg_path:
            return PickedPrompt(prompt=None, source=PromptSource.LUCIDE,
                                lucide_svg_path=svg_path)

    # Step 2: icons.csv keyword match (non-Lucide) → generic codex prompt
    if row:
        return PickedPrompt(..., source=PromptSource.ICONS_CSV)

    # Step 3: generic codex prompt
    return PickedPrompt(..., source=PromptSource.GENERIC)
```

`lucide-fetcher.py`:
- Downloads `https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/<name>.svg` (ISC license, free)
- Caches in `~/.cache/landing-system/lucide/<name>.svg`
- Renders to PNG via Pillow (или cairosvg если установлен) с правильным размером 1024x1024 + brand color
- Сохраняет в `07d_VISUALS/icons/<slot>.png` напрямую (без codex)

В `codex-generate-icon.sh` добавляется проверка: если `PromptSource.LUCIDE` — копировать SVG/PNG и exit без codex.

### Auto-fix mechanism

```python
AUTO_FIXES = {
    "prototype_yaml_exists": lambda p: run_command(f"/landing-prototype --project {p}"),
    "wireframe_html_exists": lambda p: run_command(f"/landing-wireframe --project {p}"),
    "composed_html": lambda p: run_command(f"/landing-compose --project {p}"),
    "visuals_generated": lambda p: run_command(f"/landing-visuals --project {p}"),
    "composed_has_real_visuals": lambda p: run_command(f"/landing-compose --project {p}"),
}
```

При failed гейте, если fix_hint начинается с `auto_fix:`:
1. Парсим action из hint
2. Запрашиваем confirm (или skip если `--auto-fix yes`)
3. Выполняем action
4. Re-run gate-check для того же check_id
5. Если passed — продолжаем, если failed — escalate.

### Codex CLI install (в onboarding)

`scripts/install-codex.sh`:
```bash
#!/usr/bin/env bash
if command -v codex >/dev/null 2>&1; then
    echo "✅ codex CLI уже установлен ($(codex --version))"
else
    echo "→ codex CLI не найден. Устанавливаю через npm..."
    npm i -g @openai/codex || {
        echo "❌ npm install failed. Установи вручную: npm i -g @openai/codex"
        exit 1
    }
fi

if ! codex auth status >/dev/null 2>&1; then
    echo "→ codex не залогинен. Запускаю codex login..."
    codex login
fi

echo "✅ codex готов к работе"
```

В `landing-onboarding/SKILL.md` — добавить этот шаг в onboarding flow.

### Onboarding rewrite

Новая структура `landing-onboarding/SKILL.md`:
```markdown
1. Проверка зависимостей (Python 3.10+, bash, sips если macOS)
2. Установка codex CLI (scripts/install-codex.sh)
3. Объяснение prototype-first flow:
   > 1. Положи prototype.pdf в <project>/07_ПРОТОТИП/source/
   > 2. Запусти /landing-go
   > 3. Следуй подсказкам — оркестратор сам всё проведёт
4. Smoke test (запустить test-pipeline.sh с mock)
5. Готово.
```

---

## Step-by-step UX (полный пример)

```
$ /landing-go
👀 Смотрю состояние проекта...
Текущий этап: 07a_prototype

🎯 Что сейчас сделать:
   1. Положи prototype.pdf или .md в 07_ПРОТОТИП/source/
   2. Когда готов — напиши "готово"

> готово

⚙️ Запускаю prototype-importer...
✅ prototype.yaml готов (8 блоков обнаружено)
✅ Этап 07a_prototype утверждён

📋 Следующий: 03_references
🎯 Сейчас тебе нужно: подобрать референсы.
   Открой 03_РЕФЕРЕНСЫ/index.yaml, добавь 3-5 URL.
   Или напиши "сгенерь" — я найду сам по нише.

> сгенерь

⚙️ Запускаю references-curator...
✅ Найдено 5 референсов
✅ Этап 03_references утверждён

📋 Следующий: 04_brand
[...etc...]

📋 Этап 07c_composed утверждён.

⚡ Запускаю параллельно:
   - 07d_photos (photo-curator)
   - 07e_visuals (visual-curator)

[оба subagent работают одновременно]

✅ 07d_photos готов (45 фото обработаны)
✅ 07e_visuals готов (12 иконок: 8 из Lucide, 4 через codex)

📋 Следующий: 07f_composed_final
⚙️ Re-render composed.html с реальными визуалами...
✅ Готово

📋 Следующий: 08_build
⚙️ Запускаю wp-builder...
[...]
✅ wp-theme собран. PHP синтаксис валиден. Gutenberg blocks ok.

📋 Следующий: 09_deploy
🎯 Введи hostname и SSH credentials для Бегет:
   [hostname]: example.beget.com
   [ssh user]: u123456

⚙️ Деплоим через rsync + wp-cli...
✅ Сайт доступен: https://example.beget.com
   HTTP 200 OK

🎉 Все этапы завершены. Можешь открыть сайт в браузере.
```

---

## Error handling и edge cases

| Сценарий | Поведение |
|---|---|
| Пользователь запускает `/landing-go` без prototype.pdf | Гейт 07a fails → instructions «положи prototype.pdf в 07_ПРОТОТИП/source/» |
| 03_references — пользователь не хочет добавлять | Auto-fix: `references-curator` с дефолтными референсами по нише |
| 05_design — wp-builder упал из-за невалидного PHP | Gate-check 08_build детектит, fix_hint показывает logs path, предлагает re-run wp-builder |
| 07d_photos и 07e_visuals — один упал, второй ok | Оркестратор показывает который и предлагает retry только упавшего |
| 09_deploy — SSH connection failed | Gate-check `site_url_accessible` fails, показывает curl error, fix_hint = «проверь Бегет credentials в `.beget-config`» |
| Маркетолог хочет повторить только 07d_photos руками | Запускает `/landing-photos --force-stage match` напрямую (PR-B механизм работает) |
| Lucide SVG не скачался (offline) | Fallback на codex generic generation |
| State.yaml повреждён | gate-state.sh даёт понятную ошибку + предлагает `cp .landing-state.yaml.bak` (если есть бэкап) |

**Логирование:** все оркестратор-вызовы пишутся в `07c_PHOTOS/.logs/` (для consistency со существующими PR-A/B/C логами). Можно отдельный `.orchestrator-logs/` если предпочтительнее.

---

## Testing strategy

| Что | Чем | Сценарий |
|---|---|---|
| `derive-landing-structure.py` | pytest | prototype.yaml с 8 блоками → landing-structure.md с правильным «Контракт с wp-builder» |
| `lucide-fetcher.py` | pytest | hint=menu → fetches Lucide SVG → конверт в 1024×1024 PNG с brand color |
| `prompt-picker.py` Lucide branch | pytest | hint=menu + icons.csv→Library=Lucide → returns PromptSource.LUCIDE |
| gate-check status `n/a` | bats | state.yaml со status=n/a → gate-check не валит require_approved |
| `verify-composed-has-visuals.sh` | bats | composed.html с `[SLOT:` → exit 1; без → exit 0 |
| `verify-php-syntax.sh` | bats | dir с broken PHP → exit 1; valid → exit 0 |
| `verify-gutenberg-json.sh` | bats | invalid block.json → exit 1 |
| Auto-fix flow | bats | mock failed gate → auto_fix hint → execute → re-check pass |
| Parallel dispatch | bats (integration) | mock 07d + 07e subagents → both run, both finish, transition to 07f |
| `/landing-go` next-stage detection | bats | state.yaml с partial completion → correct next stage |
| `install-codex.sh` | bats | mock codex absent → reports «would install»; present → reports «already installed» |
| `landing-onboarding` updated | bats | grep new flow text |
| E2E PR-D pipeline | bats (test-pipeline.sh extension) | full prototype-first flow with mocks → проходит без падений |

**Объём:** ~25-30 новых тестов. Mock codex переиспользуется из PR-B.

---

## Acceptance criteria

- [ ] `/landing-go` на пустом проекте (только prototype.pdf) → доводит до 07f без ручных команд (кроме 03/04/05/07b)
- [ ] Все 7 новых stages в `template/.landing-state.yaml`
- [ ] `n/a` status работает (gate-check пропускает)
- [ ] Параллельный 07d+07e — обe agent одновременно
- [ ] Auto-fix на 5+ простых ошибках работает
- [ ] Lucide branch вызывается для `menu`, `arrow-left`, `shield` (из icons.csv с Library=Lucide) → не зовёт codex
- [ ] Codex install скрипт работает: устанавливает если нет, пропускает если есть
- [ ] Landing-onboarding объясняет prototype-first flow
- [ ] PR-A + PR-B + PR-C регрессионные тесты не падают (>200 тестов)
- [ ] 25+ новых тестов проходят
- [ ] E2E test-pipeline.sh + PR-D stage проходит с mock
- [ ] THIRD_PARTY_NOTICES.md обновлён (Lucide ISC)
- [ ] CLAUDE.md обновлён с `/landing-go` workflow

---

## Dependencies

- `codex` CLI v0.125+ (auto-installed via install-codex.sh)
- Python 3.10+ + Pillow + PyYAML + BeautifulSoup4 + (optional) cairosvg
- Node.js + npm (для install-codex.sh — `npm i -g @openai/codex`)
- bash + bats для shell тестов
- `superpowers:dispatching-parallel-agents` skill
- Internet (для Lucide SVG fetch + codex login)

Никаких новых external API.

---

## Known risks

### R1 — Параллельная диспетчеризация может конфликтовать на shared state

07d_photos пишет в `07c_PHOTOS/STATE.yaml`. 07e_visuals пишет в `07d_VISUALS/STATE.yaml`. Это разные файлы → конфликта нет. Но: оба читают `tokens.json` (только чтение) и пишут в свои логи (разные dirs) → safe.

**Mitigation:** убедиться что photo-curator и visual-curator не пишут ни в один общий файл.

### R2 — Lucide CDN может быть недоступен

`raw.githubusercontent.com` может быть заблокирован в РФ или временно down.

**Mitigation:** lucide-fetcher.py имеет timeout 5s + fallback на codex generic. Также cache в `~/.cache/landing-system/lucide/` — после первого скачивания работает offline.

### R3 — Auto-fix может зациклиться

Если auto_fix запускает action который снова падает → infinite loop.

**Mitigation:** max 1 auto-fix attempt per check_id per `/landing-go` invocation. После — escalate с понятным сообщением.

### R4 — wp-builder ожидает 01a_АНАЛИЗ_НИШИ/landing-structure.md но мы skip 01a

**Mitigation:** `derive-landing-structure.py` (Task 4) создаёт этот файл из prototype.yaml. wp-builder работает unchanged.

### R5 — `n/a` status может сломать существующие тесты

gate-check.sh / gate-state.sh код тестируется только на known статусы (locked/in_progress/approved/failed).

**Mitigation:** обновить тесты в `tests/gate-check/` чтобы покрывали `n/a` case.

### R6 — Codex CLI install требует root permissions для global npm

`npm i -g` может потребовать sudo на некоторых системах.

**Mitigation:** скрипт detects EACCES и предлагает `sudo npm i -g` или `npx @openai/codex` fallback.

---

## Migration / backward compatibility

- Существующие проекты с `.landing-state.yaml` без 07a/b/c/d/e/f → миграционный скрипт `scripts/migrate-state-for-prd.sh` добавляет недостающие stages со status=locked.
- PR-A/B/C артефакты — не трогаем
- Существующие slash-команды — остаются как direct entry points
- `gate-check.sh` — расширяется, не переписывается
- `landing-orchestrator.md` — добавляется новый раздел «Phase 6: Prototype-first flow» рядом с существующими

---

## Attribution

Обновить `THIRD_PARTY_NOTICES.md`:

```
## Lucide icons (ISC License)

PR-D (2026-05-13) integrates Lucide icons (https://lucide.dev) as a fallback
source for simple icon slots. lucide-fetcher.py downloads SVG files from the
official repo and converts them to brand-colored PNGs.

License: ISC. Original repo: https://github.com/lucide-icons/lucide
Icons used: any from `icons.csv` row where `Library=Lucide`.
```

---

## Open questions / future PRs

- **PR-E** — Усиление `design-system-generator` через 149 OpenDesign DESIGN.md
- **PR-F** — Polish block-library templates через OpenDesign skill-block-template
- **PR-G** — Web UI поверх /landing-go
- **PR-H** — Multilingual (RU + EN)
- **Telemetry** — анонимная статистика какие auto-fix чаще срабатывают (для приоритезации улучшений)
