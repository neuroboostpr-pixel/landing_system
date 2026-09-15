# End-to-End Functional Risk Audit (v2-05)

**Date:** 2026-05-20
**Methodology:** system integration audit — «что может помешать системе выпустить лендинг», не code-review
**Branch:** `feat/audit-top10-fixes` (HEAD = `a4bcf7c`)
**Reviewer mindset:** QA lead с задачей «отдать системе 10 проектов и не пожалеть».

---

## Mission (5 предложений)

`landing-system` — мастер-агентская система производства WordPress-лендингов для агентства лидогенерации. Маркетолог кладёт `prototype.pdf` в папку нового проекта и запускает `/landing-start` или `/landing-go`; оркестратор ведёт его через ~20 этапов (00 бриф → 12 SEO) с user-interactive HARD GATEs после каждого. На каждом этапе срабатывает специализированный агент: парсит прототип, делает мудборд, бренд-кит, design-tokens, wireframe, composed.html (premium-стандарт из 13 фич), генерирует фото и иконки через `codex` CLI, собирает Lazy-Blocks WP-тему, деплоит на Бегет через SSH/wp-cli, прогоняет QA и пишет метатеги. State хранится в `<project>/.landing-state.yaml`; гейты проверяются `scripts/gate-check.sh` по `config/stage-gates.yaml`, а `scripts/hooks/enforce_stage_gate.py` физически блокирует Write/Edit к файлам стадии, чьи предшественники не `approved`/`n/a`. Цель — за один проход от прототипа до живого URL с метрикой, CRM-webhook'ом и premium-визуалом, без ручного PHP-кодинга.

---

## Pipeline stages × external dependencies × gating

| Stage | External deps | Checked at runtime? | Failure mode (что увидит маркетолог) |
|---|---|---|---|
| 00 brief | — | n/a | low risk, ручной |
| 01 context | — | n/a | low risk |
| 01a niche_analysis | Firecrawl + Anthropic SDK auth (`~/.claude/auth.json`) | partial — `validate-all.sh` проверяет Firecrawl, SDK auth — нигде | если auth протух → agent кидает SDKError, flush.py молча проглатывает, niche-analyst скорее всего тоже упадёт без понятного error |
| 02 assets | хотя бы один из PEXELS/UNSPLASH/PIXABAY | ✅ gate `api_validator_any_of` | clear error из `validate-all.sh` |
| 03 references | Firecrawl (опц.) | нет dedicated check | если Firecrawl недоступен — references-curator пишет пустой `index.yaml`, гейт ловит только наличие файла |
| 04 brand | — | ✅ `brand-kit.md` exists | low risk |
| 05 design | — | ✅ `DESIGN.md` + `tokens.json` exist | контент-проверки нет (поля токенов могут быть кривые) |
| 06 stack | iconify.design, fonts.bunny.net, cdn.jsdelivr.net | ✅ `http_ping` ×3 | при отсутствии сети маркетолог застрянет на 06 |
| 07 content | — | ✅ `final-copy.md` exists | контент-валидации нет |
| 07a prototype | — | ✅ `file_or_dir_exists` (fix #3 done) | OK |
| 07b wireframe | — | ✅ `wireframe.html` + `selections.yaml` | OK — но `selections.yaml` маркетолог должен скачать и положить вручную (UX-trap) |
| 07c composed | `verify-composed-premium.sh`, `verify-content-preserved.sh`, `verify-photo-pipeline.sh` | ✅ 4 hard checks | premium-gate отлично работает; верифит запускается **дважды** (silent + verbose) — недетерминированные verify могут глючить |
| 07d photos | **`codex` CLI** (`@openai/codex` npm), PIL/bs4/yaml | **❌ codex наличие не проверяется в гейте 07d!** | если codex не установлен — `photo-curator` упадёт mid-stage с непонятной ошибкой; маркетолог не получит подсказку `bash scripts/install-codex.sh` |
| 07e visuals | **`codex` CLI** + Anthropic SDK для image_gen | **❌ codex не gate-checked** | то же — silent crash mid-stage |
| 07f composed_final | `verify-composed-has-visuals.sh` (regex `[SLOT:` / `[INFOGRAPHIC:`) | ✅ | regex не ловит русские placeholder-варианты `[ИКОНКА:]` если block-composer их вставит |
| 08 build | **`php` CLI** для `verify-php-syntax.sh`, Python+PyYAML | partial — `verify-php-syntax.sh` exit 2 при отсутствии php (= ✅ для gate!) | ⚠️ **silent pass** — php-syntax check возвращает exit 2 «warning» вместо fail, и сборщик ловит exit 2 как непрошедшую проверку (но fix_hint молчит про «установи php») |
| 08b style | — | partial — `block-php-markers`, `section5-has-css` | нормально |
| 09 deploy | `wp-cli` (remote через ssh), `rsync`/`scp`, `ssh` ключи к Бегету, **активный сайт на Бегете с установленным WP**, BEGET_USER/HOST/PATH | ✅ ssh ping + ym + telegram + crm | beget API/SSL/DNS — отдельная проблема; нет проверки что WP уже установлен на target |
| 10 qa | — | soft only (один вопрос «yes/no») | qa-auditor может скипать |
| 11 analytics | yandex-metrika OAuth | проверяется только в 09 deploy, не в 11 | если токен умер между этапами — silent |
| 12 seo | — | ✅ `meta-tags.yaml` | low risk |

---

## 🔴 BLOCKERS (физически могут сорвать выпуск лендинга)

### B1. `codex` CLI — главная скрытая зависимость, не gate-checked
**Где:** `config/stage-gates.yaml:254-274` (стадии `07d_photos`, `07e_visuals`), `scripts/install-codex.sh` есть, но никто из гейтов его не вызывает.
**Impact:** ~50% pipeline (фото + иконки + инфографика) полностью полагается на `codex`. Если маркетолог пропустил `bash scripts/install-codex.sh` в онбординге (а онбординг сам по себе опциональный шаг, см. B3) — упадёт **mid-stage** в `photo-curator` или `visual-curator`. Сообщение будет «codex: command not found», без указания, как чинить. У оркестратора **нет auto-fix `bash scripts/install-codex.sh`** для этого случая.
**Доп.:** `codex login` тоже отдельный шаг. Если npm install прошёл, но login нет — `photo-curator` отправит запрос и получит 401, агент его не интерпретирует.
**Fix:** добавить в `01a` или `02_assets` (или в новый «stage 00 preflight») hard_check `type: script` который зовёт `bash scripts/install-codex.sh --check` + `codex auth status`. Сделать fix_hint `auto_fix: bash scripts/install-codex.sh`.

### B2. PreToolUse hook fail-open + `.claude/settings.local.json` `bypassPermissions`
**Где:** `scripts/hooks/enforce_stage_gate.py:108-119` — любая exception разрешает edit; `.claude/settings.local.json` (упомянуто в audit/04, на момент аудита) — `bypassPermissions: true` + `skipDangerousModePermissionPrompt: true`.
**Impact:** «physical enforcement» теоретически работает, но (а) corrupt YAML / unwriteable `_stage_paths.yaml` / pip yaml import failure → hook молча пропускает all writes, (b) если пользователь редактирует через свой Claude Code с `bypassPermissions`, hooks по контракту Anthropic могут не запускаться или эффект другой. Это **не «policy is law»**, это «policy если повезло».
**Fix:** добавить health-check «hook действительно сработал» — например, при `current_stage = 05_design` попробовать Write в `08_КОД/test.txt` и ассертить, что хук блокирует; включить в `landing-final-check.sh` или smoke-test.

### B3. Onboarding не обязателен — `preflight.sh` зовут только из `deploy.sh`
**Где:** `scripts/preflight.sh:9-12` — проверяет `setup-flag.sh is_complete` и завершает с ошибкой. **Но** `preflight.sh` запускается только из `scripts/deploy.sh:14-18` (этап 09). Команды `/landing-go`, `/landing-photos`, `/landing-visuals`, `/landing-build` его НЕ вызывают.
**Impact:** маркетолог может пропустить весь онбординг (нет `.env`, нет валидации ключей, нет codex), запустить `/landing-go`, и система начнёт делать этапы, падая на каждом по-разному. Падение случится только на 09 deploy, через 1-2 часа работы.
**Fix:** добавить `bash "$REPO_ROOT/scripts/preflight.sh" || exit 1` в начало `/landing-go` (или в каждый агент-pipeline в pre-flight phase).

### B4. `gate-check.sh:script` runner запускает script ДВАЖДЫ
**Где:** `scripts/gate-check.sh:247-263` — `if $runner ... >/dev/null 2>&1` затем второй раз `$runner ... 2>&1 | sed`.
**Impact:** verify-скрипты с побочными эффектами выполняются дважды (двойные codex-вызовы, двойные генерации фото, удвоенный токен-бюджет). Недетерминированные verify (`verify-photo-pipeline.py` зовёт PIL, `verify-visual-qa.sh` дёргает Playwright) могут пройти первый раз и упасть второй или наоборот; в логе пользователь увидит несоответствие. Этот баг **известен** (audit/04 Critical-3 от 2026-05-20), но **НЕ исправлен в Phase 1-5** — `gate-check.sh` всё ещё содержит double-run.
**Fix:** один прогон в `mktemp`, `cat` при fail.

### B5. Анти-recursion в post-commit смотрит только на `chore(wiki)` — авто-коммит может зациклиться
**Где:** `.githooks/post-commit:13-15` — `case "$LAST_MSG" in chore\(wiki\)*) exit 0`. Защита OK для wiki-cycle, **но** хук авто-коммитит `wiki/index.md wiki/log.md wiki/concepts/ wiki/preview.html`. Если `wiki/concepts/<X>.md` содержит non-deterministic timestamp от SDK — каждый запуск SDK даёт новый хэш → новый коммит → новый run хука → новый коммит. Защита от `chore(wiki)` сработает на 2-м цикле, но 1 лишний коммит появится **каждый раз**.
**Impact:** замусоривание git history; на больших репо медленно. Не блокер для одного лендинга, но при mass testing 10+ проектов — ощутимая боль.
**Fix:** добавить guard «wiki/log.md не считать в диффе» или `git diff --stat` и пропускать если меняется только дата.

---

## 🟡 DEGRADERS (система работает, но больно)

### D1. Anthropic SDK auth не проверяется в onboarding
**Где:** `tools/api_validators/` содержит 15 validators, но Anthropic SDK auth (через `~/.claude/auth.json` или `ANTHROPIC_API_KEY`) — нет. `scripts/wiki/sdk_client.py:52` использует `max_turns=50`, что в случае «забыли залогиниться» приведёт к 50 неудачным попыткам.
**Impact:** wiki-compile + flush.py молча падают (`except SDKError: return`). Маркетолог видит «всё ок», но wiki не обновляется и lessons learned не пишутся. Также `niche-analyst` и `block-composer` зависят от SDK — они кидают понятную ошибку только в нескольких местах.
**Fix:** добавить `tools/api_validators/anthropic_sdk.py` + включить в `validate-all.sh` + в `preflight.sh`.

### D2. `verify-php-syntax.sh` возвращает exit 2 при отсутствии PHP
**Где:** `scripts/verify-php-syntax.sh:21-24` — `WARN: php CLI not installed — skipping PHP syntax check >&2; exit 2`.
**Impact:** `gate-check.sh` трактует **любой ненулевой exit** как fail. Маркетолог увидит «❌ theme_php_syntax_valid: script ... failed» без объяснения «надо `brew install php`». Скорее всего застрянет.
**Fix:** в `check-deps.sh` явно проверять `php` (сейчас проверяет `bats`, `git`, `node`, `bash`); или менять gate-fix-hint на конкретную инструкцию.

### D3. Beget WP не валидируется ДО deploy
**Где:** `tools/api_validators/beget_ssh.py` — только `ssh echo ok`. `tools/api_validators/beget_api.py` — отдельная история. **Никто** не проверяет: (а) что на хосте установлен WordPress, (б) что доменная зона указывает на хост, (в) что есть SSL, (г) что mysql работает, (д) что `wp-cli` доступен по ssh.
**Impact:** в `deploy-wordpress.sh:38-39` команда `wp theme activate lp-${SLUG}` упадёт, если WP не инициализирован — маркетолог получит wp-cli stderr посреди деплоя.
**Fix:** добавить hard_check в 09_deploy: `ssh ... 'cd $BEGET_PATH && wp core is-installed'`.

### D4. Никто не валидирует размер/sanity prototype.pdf
**Где:** `prototype-importer` агент парсит PDF; если PDF на 200 страниц с картинками — упадёт по таймауту или памяти SDK. Гейт 07a `prototype_yaml_exists` сработает только после успешного парсинга.
**Impact:** маркетолог положит PDF от клиента (часто 50+ MB с фотками), `/landing-prototype` крутится 10+ минут, рискует таймаутом SDK, retry-стратегии нет.
**Fix:** добавить prep-check `file_size < 10MB && pdfinfo pages < 30`.

### D5. `wiki/.cache.json` + system_compiler — broken-source hash *теперь* кэшируется (фикс #6 сделан), но удалить broken-source хэш можно только руками
**Где:** `scripts/wiki/system_compiler.py:179-188` — при `SDKError` пишет hash в кэш. **Это правильное поведение** (не зовём SDK снова), но если SDK упал из-за временной ошибки (rate-limit, network), broken-source застрянет в кэше пока пользователь руками не отредактирует source-файл. `errors[]` показывается, но silent для casual user.
**Impact:** деградация качества wiki — concept-файл устарел, но никто не знает.
**Fix:** добавить TTL для error-кэша (через 24h re-run) или `--clear-errors` flag.

### D6. Wiki SDK_CLIENT с `max_turns=50` — token bleed
**Где:** `scripts/wiki/sdk_client.py:53` — `max_turns=50` для **каждого** концепта (а их 200+ блоков, 33 агента, 24 скилла = 250+ запросов).
**Impact:** один файл compile = до 50 turns × ~2k tokens = 100k tokens. Полный rebuild = 25M+ tokens. Известная проблема (Top-10 #4, Cluster C), **не исправлена**.
**Fix:** `max_turns=1` — compile концепта это single-shot generation, не agentic loop.

### D7. Все 33 агента содержат идентичный 25-строчный Stage Execution Protocol preamble
**Где:** все `agents/*.md`. Каждый запуск sub-agent — этот текст уходит в context window.
**Impact:** ~800 tokens overhead per dispatch × 20 этапов = 16k tokens на проект только на preamble. Тиражирование сделано (Top-10 #2 ✅), но без shared template/include — изменение протокола требует bulk-edit.
**Fix:** вынести в `agents/_protocol.md`, в каждом агенте — 1 строка `## Stage Execution Protocol → [_protocol.md]`.

### D8. `landing-final-check.sh` использует `eval` на user-supplied path
**Где:** `scripts/landing-final-check.sh:33` — `OUTPUT=$(eval "$CMD" 2>&1)`. `$CMD` собирается из массива с single-quoted `$PROJECT`. Если project path содержит `$(...)` или backticks, это будет исполнено.
**Impact:** маркетологи кладут проекты в `~/Lendings/имя-кириллицей/` — пути обычно безопасные. Но это явный **code-injection vector**. Известно (audit/02 Cluster D), не исправлено.
**Fix:** `bash -c "$CMD"` или массивный exec вместо `eval`.

---

## 🟢 EDGE CASES

- **E1.** `.githooks/post-commit` пропускает (`exit 0`) во время `rebase/merge/cherry-pick` — корректно, но «забывает» переразвернуть wiki после завершения rebase. Wiki останется stale до следующего обычного коммита.
- **E2.** `enforce_stage_gate.py` `_find_project_root` поднимается вверх по `.landing-state.yaml`. Если редактируешь файл вне `~/Lendings/<slug>/` (например, в `landing-system/`) — хук всегда возвращает 0. Корректно, но не проверяет, что landing-system сам не содержит «фейковый» `.landing-state.yaml` для тестов.
- **E3.** `gate-check.sh` `http_ping` `--max-time 10` — на медленном интернете 06_stack упадёт из-за iconify/bunny/jsdelivr. Маркетолог не поймёт, что это сеть.
- **E4.** `verify-composed-has-visuals.sh` ищет `[SLOT:`, `[INFOGRAPHIC:`, `[photo slot:` — но `block-composer` может вставить русские/локализованные placeholder'ы (видел `[ИКОНКА:` в одном из агентов).
- **E5.** `gate-check.sh:299-303` — после soft-check fail НЕ показывает `fix_hint` (только для hard).
- **E6.** `verify-composed-premium.sh` parallax-regex `(scrollY|[^a-zA-Z_0-9]y)\s*\*\s*0\.[0-9]` ловит **любое** умножение `y * 0.x` в JS (например `let y = top * 0.5` для какого-то расчёта высоты) — false-positive pass.
- **E7.** `01a_niche_analysis` сейчас требует **10** обязательных файлов с валидаторами (3 visual-requirements, market-profile, positioning, landing-structure). Если niche-analyst упадёт на 7-м — нет частичного approve. Всё или ничего.
- **E8.** `template/.landing-state.yaml` ставит `07a_prototype: in_progress` по умолчанию. Если маркетолог положит PDF, но забудет `/landing-prototype` — состояние «в работе» висит, никто не двигает.

---

## Critical untested user paths

| Path | Зачем важно | Как протестировать |
|---|---|---|
| **CP1.** Full happy-path: `/landing-start` → `/landing-go` → live URL на Бегете на одном проекте | главный sales-story системы | нужен test Бегет-аккаунт; запустить `tests/phase-pra/fixtures/prototype-sample.md` end-to-end с реальным деплоем |
| **CP2.** Prototype-first без onboarding'а (свежая машина, .env пустой) | проверка graceful failure | docker-контейнер без codex/.env, запустить `/landing-go`, ожидаемо — fail-fast с понятным сообщением. Сейчас не fail-fast |
| **CP3.** Параллельная диспетчеризация 07d ⇆ 07e | конкурентность файловой системы | оба пишут в `composed.html` (re-render); race-condition? Никаких file-locks в коде не видел |
| **CP4.** `/landing-clone <new-slug>` | A/B-копия — заявленная фича | агент `lifecycle-keeper` существует, скилл `landing-versioning-and-cloning` есть, **smoke-test не нашёл** |
| **CP5.** `/landing-rollback v1.0` | recovery — заявленная фича | то же, скилл есть, тесты не видны |
| **CP6.** Mass restart: запустить `/landing-go` 3 раза подряд (имитация падения процесса) | resume должен быть идемпотентным | `landing-go-next-stage.py` детерминирован, но `photo-curator/visual-curator` могут не быть |
| **CP7.** Corrupt `.landing-state.yaml` mid-run | recovery | fail-open хука разрешит edit, `gate-check.sh` сломается на `yq` — что увидит маркетолог? |
| **CP8.** PreToolUse hook на компе пользователя где Python без `yaml` | recovery | хук молча allow → enforcement сломан → агент перепрыгивает стадии. Нужен health-check |
| **CP9.** Beget вернул 502 mid-deploy | rollback path | `deploy.sh` упадёт на половине; что с remote state? wp theme already activated? |
| **CP10.** Codex API rate-limit во время /landing-visuals на 20-й иконке | retry/resume | unknown — нет видимого retry-кода |

---

## Verdict

### Production-ready for SOLO operator (1 landing)?
**ДА, с оговорками.** Если оператор сам собрал систему (знает codex, php, wp-cli, .env заполнен), помнит про preflight, не редактирует state.yaml руками — happy path работает. Top-10 phase 1-5 фиксов сняли самые острые углы (legacy bypass, unknown check types, hash-cache O(N²), preTool hook, протоколы во всех агентах).

### Ready for MASSIVE TESTING (10+ landings, mixed flows, новые операторы)?
**НЕТ.** Три barriers:

1. **Onboarding не enforced** — новый оператор пропустит `setup_complete`, `codex login`, `.env`, и узнает об этом через 1-2 часа на этапе 07d или 09. UX-катастрофа при mass testing.
2. **Codex не gate-checked** — половина pipeline зависит от внешнего CLI, который никто не проверяет до момента использования. Massive testing = 10/10 проектов могут upасть mid-stage без понятной причины.
3. **`gate-check.sh script` runner ×2** — double-execution скриптов с побочками (codex, Playwright) удвоит token-бюджет и сломает недетерминированные verify. На 10+ проектах = $$$ + flaky tests.

### Top-3 blockers to fix before mass testing

| # | Fix | Effort | Impact |
|---|---|---|---|
| **1** | Добавить hard_check на `codex` CLI + `codex auth status` в 02_assets (или в новую stage `00_preflight`). Fix_hint: `auto_fix: bash scripts/install-codex.sh` | 30 мин | Закрывает B1 + значительно облегчает onboarding |
| **2** | Сделать `bash scripts/preflight.sh` обязательным в начале `/landing-go` (и в каждом stage-агенте). Без `setup_complete` flag — refuse to start | 30 мин | Закрывает B3, делает onboarding mandatory |
| **3** | Починить double-run `script` runner в `gate-check.sh:247-263` через mktemp | 15 мин | Закрывает B4, экономит токены и снимает flakiness |

После этих трёх — система готова к 5-10 проектам параллельно. Для 50+ проектов нужны ещё D1 (Anthropic SDK validator), D2 (php в check-deps), D3 (WP-on-Beget pre-deploy check), и проверка CP3 race-condition в 07d⇆07e.

---

## Сухой остаток

Система **сделана грамотно** на уровне архитектуры: data-driven gates, версионируемый state, premium-checklist, fail-open хук, кеширование, validate-all для 15 сервисов. Phase 1-5 фиксы закрыли все top-10 из первого аудита.

Но **дисциплина «не пропускать шаги»** держится на трёх ножках, две из которых трещат при mass testing:

1. ✅ Хук `enforce_stage_gate.py` — работает, но fail-open + не health-checked.
2. ✅ Преамбула во всех 33 агентах — есть, но это инструкция, не блокировка.
3. ❌ `preflight.sh` + `codex install` + `.env` validation — **не обязательны**, не вызываются автоматически до начала работы. Это **самая большая дыра** для нового оператора.

«Что может помешать» — в порядке убывания вероятности:
1. Свежая машина без `codex` → fail mid-photos
2. `.env` без BEGET_*/PEXELS_* → fail на 02 или 09
3. PHP не установлен → fail на 08_build (silent gate-pass с exit 2)
4. SDK auth протух → wiki+flush молча умирают, niche-analyst мутно падает
5. Beget WP не инициализирован → deploy crash после rsync (грязное состояние на хосте)
6. Кириллический prototype.pdf на 50MB → таймаут SDK на 07a
7. Race 07d⇆07e → composed.html corrupted (untested)
8. Corrupt state.yaml → fail-open хук разрешит всё, дисциплина исчезнет

Чинить в порядке Top-3 выше → массовое тестирование станет реально, а не «попробуем и посмотрим».
