# Phase 0 — Reference Map

**Дата:** 2026-05-23  
**Скоуп:** полная reference-map репозитория landing-system  
**Инструмент:** code-reviewer skill (read-only: Read, Grep, Glob) + Python-аналитика для построения графа ссылок

## Executive Summary (для руководства)

Просканировано всего 723 файлов из 15 категорий (скиллы, агенты, команды, скрипты, конфиги, стандарты качества, шаблонные README, мета-описания блоков библиотеки, файлы mu-плагина WordPress, авто-документация скриптов, git-хук). Из них 414 имеют хотя бы одну ссылку из исполняемого слоя (агенты / команды / скрипты / PHP-инклюды mu-плагина), 309 упоминаются только в документации (wiki, docs, README, CLAUDE.md), 0 не имеют видимых ссылок ниоткуда.

Папка слеш-команд (`commands/` в корне репо и `.claude/commands/`) содержит расхождения по 4 командам — это пары файлов, отличающиеся по наличию в одной из папок или по содержимому. Зафиксировано 21 скриптов с признаками миграции, 11 файлов с префиксом подчёркивания, 80 пар «исполняемый-скрипт / `.doc.md`-сопроводитель» (из них 0 без существующего исполняемого файла).

Дополнительно выявлено 439 пар файлов с пересекающимися токенами в именах; список вынесен в `phase-0-suspicious-duplicates.md` для обсуждения в фазе 1. Никаких решений по удалению/слиянию в фазе 0 не принимается — это диагностика.

## Метрики

- Просканировано всего файлов: **723**
- Раскладка по `usage_class`:
  - `active` (есть ссылка из исполняемого слоя): **414**
  - `doc-only` (упоминание только в документации): **309**
  - `orphan` (0 ссылок ниоткуда): **0**
- Расхождений между папками команд `.claude/commands/` ↔ `commands/`: **4**
- Migration-скриптов: **21**
- Файлов с префиксом `_`: **11**
- `.doc.md` пар: **80** (из них с отсутствующим исполняемым файлом: **0**)
- Пар файлов с пересекающимся токеном (для фазы 1): **439**

### Раскладка по категориям

| Категория | Всего | active | doc-only | orphan |
|---|---:|---:|---:|---:|
| `agent` | 33 | 33 | 0 | 0 |
| `block-meta` | 190 | 66 | 124 | 0 |
| `command-dot-claude` | 32 | 32 | 0 | 0 |
| `command-root` | 29 | 29 | 0 | 0 |
| `config` | 3 | 3 | 0 | 0 |
| `git-hook` | 1 | 1 | 0 | 0 |
| `mu-plugin-php` | 56 | 49 | 7 | 0 |
| `pattern-meta` | 22 | 0 | 22 | 0 |
| `script` | 91 | 70 | 21 | 0 |
| `script-doc` | 80 | 0 | 80 | 0 |
| `skill` | 27 | 27 | 0 | 0 |
| `skill-script` | 116 | 96 | 20 | 0 |
| `standard` | 4 | 2 | 2 | 0 |
| `style-guide` | 6 | 6 | 0 | 0 |
| `template-readme` | 33 | 0 | 33 | 0 |

## Полный список candidate-файлов

Отсортирован по убыванию числа исходящих ссылок (`outgoing_refs_count`). Все файлы без обрезки.

| Путь | Категория | usage_class | Входящих | Исходящих |
|---|---|---|---:|---:|
| `agents/landing-orchestrator.md` | agent | active | 707 | 63 |
| `config/stage-gates.yaml` | config | active | 319 | 55 |
| `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` | mu-plugin-php | active | 92 | 45 |
| `.claude/commands/landing-build.md` | command-dot-claude | active | 397 | 32 |
| `commands/landing-build.md` | command-root | active | 397 | 32 |
| `.claude/commands/landing-help.md` | command-dot-claude | active | 72 | 30 |
| `commands/landing-help.md` | command-root | active | 72 | 30 |
| `.claude/commands/landing-go.md` | command-dot-claude | active | 268 | 24 |
| `commands/landing-go.md` | command-root | active | 268 | 24 |
| `docs/standards/stage-execution-protocol.md` | standard | active | 94 | 22 |
| `scripts/test-pipeline.sh` | script | active | 60 | 22 |
| `agents/photo-curator.md` | agent | active | 403 | 21 |
| `agents/niche-analyst.md` | agent | active | 222 | 18 |
| `skills/landing-onboarding/SKILL.md` | skill | active | 317 | 17 |
| `skills/wp-gutenberg-block-builder/SKILL.md` | skill | active | 256 | 17 |
| `agents/visual-curator.md` | agent | active | 193 | 17 |
| `agents/brand-architect.md` | agent | active | 318 | 16 |
| `skills/photo-curation/SKILL.md` | skill | active | 189 | 16 |
| `agents/prototype-importer.md` | agent | active | 177 | 16 |
| `scripts/generate-wp-blocks.py` | script | active | 92 | 16 |
| `template/README.md` | template-readme | doc-only | 6 | 16 |
| `.claude/commands/landing-design.md` | command-dot-claude | active | 220 | 15 |
| `commands/landing-design.md` | command-root | active | 220 | 15 |
| `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` | skill-script | active | 135 | 15 |
| `.claude/commands/landing-style.md` | command-dot-claude | active | 70 | 15 |
| `commands/landing-style.md` | command-root | active | 70 | 15 |
| `agents/ux-composer.md` | agent | active | 885 | 14 |
| `agents/landing-onboarding-wizard.md` | agent | active | 71 | 14 |
| `.claude/commands/landing-visuals.md` | command-dot-claude | active | 158 | 13 |
| `commands/landing-visuals.md` | command-root | active | 158 | 13 |
| `agents/frontend-builder.md` | agent | active | 128 | 13 |
| `template/01a_АНАЛИЗ_НИШИ/README.md` | template-readme | doc-only | 56 | 13 |
| `agents/block-composer.md` | agent | active | 941 | 12 |
| `agents/style-extractor.md` | agent | active | 153 | 12 |
| `agents/design-system-generator.md` | agent | active | 278 | 11 |
| `agents/moodboard-composer.md` | agent | active | 191 | 11 |
| `skills/wireframe-rendering/scripts/match-candidates.py` | skill-script | active | 28 | 11 |
| `agents/wp-builder.md` | agent | active | 450 | 10 |
| `.claude/commands/landing-deploy.md` | command-dot-claude | active | 290 | 10 |
| `commands/landing-deploy.md` | command-root | active | 290 | 10 |
| `.claude/commands/landing-stack.md` | command-dot-claude | active | 168 | 10 |
| `commands/landing-stack.md` | command-root | active | 168 | 10 |
| `.claude/commands/landing-brand.md` | command-dot-claude | active | 162 | 10 |
| `commands/landing-brand.md` | command-root | active | 162 | 10 |
| `.claude/commands/landing-start.md` | command-dot-claude | active | 153 | 10 |
| `commands/landing-start.md` | command-root | active | 153 | 10 |
| `.claude/commands/landing-prototype.md` | command-dot-claude | active | 142 | 10 |
| `commands/landing-prototype.md` | command-root | active | 142 | 10 |
| `agents/photo-preview-board.md` | agent | active | 112 | 10 |
| `.claude/commands/landing-new.md` | command-dot-claude | active | 266 | 9 |
| `commands/landing-new.md` | command-root | active | 266 | 9 |
| `agents/references-curator.md` | agent | active | 222 | 9 |
| `.claude/commands/landing-photos.md` | command-dot-claude | active | 203 | 9 |
| `commands/landing-photos.md` | command-root | active | 203 | 9 |
| `agents/wp-deployer.md` | agent | active | 201 | 9 |
| `.claude/commands/landing-content.md` | command-dot-claude | active | 161 | 9 |
| `commands/landing-content.md` | command-root | active | 161 | 9 |
| `agents/client-assets-collector.md` | agent | active | 141 | 9 |
| `skills/wp-theme-assembler/SKILL.md` | skill | active | 124 | 9 |
| `.claude/commands/landing-moodboard.md` | command-dot-claude | active | 102 | 9 |
| `commands/landing-moodboard.md` | command-root | active | 102 | 9 |
| `agents/lifecycle-keeper.md` | agent | active | 97 | 9 |
| `scripts/landing-final-check.sh` | script | active | 35 | 9 |
| `.claude/commands/landing-compose.md` | command-dot-claude | active | 196 | 8 |
| `commands/landing-compose.md` | command-root | active | 196 | 8 |
| `skills/landing-project-init/SKILL.md` | skill | active | 164 | 8 |
| `.claude/commands/landing-references.md` | command-dot-claude | active | 153 | 8 |
| `commands/landing-references.md` | command-root | active | 153 | 8 |
| `agents/qa-auditor.md` | agent | active | 143 | 8 |
| `agents/onboarding-guide.md` | agent | active | 80 | 8 |
| `docs/standards/stage-agent-preamble.md` | standard | doc-only | 15 | 8 |
| `template/08_КОД/legal-pages/README.md` | template-readme | doc-only | 6 | 8 |
| `skills/block-composition/SKILL.md` | skill | active | 987 | 7 |
| `skills/niche-analysis/SKILL.md` | skill | active | 244 | 7 |
| `agents/seo-optimizer.md` | agent | active | 211 | 7 |
| `agents/analytics-engineer.md` | agent | active | 185 | 7 |
| `agents/integrations-engineer.md` | agent | active | 178 | 7 |
| `.claude/commands/landing-wireframe.md` | command-dot-claude | active | 172 | 7 |
| `commands/landing-wireframe.md` | command-root | active | 172 | 7 |
| `scripts/deploy.sh` | script | active | 156 | 7 |
| `agents/stack-planner.md` | agent | active | 140 | 7 |
| `skills/visual-qa/SKILL.md` | skill | active | 121 | 7 |
| `agents/scene-director.md` | agent | active | 110 | 7 |
| `scripts/wizard.sh` | script | active | 104 | 7 |
| `skills/wp-landing-config/SKILL.md` | skill | active | 64 | 7 |
| `skills/landing-from-context/scripts/from-context.sh` | skill-script | active | 47 | 7 |
| `skills/wp-multisite/SKILL.md` | skill | active | 35 | 7 |
| `skills/wireframe-rendering/SKILL.md` | skill | active | 613 | 6 |
| `agents/content-writer.md` | agent | active | 266 | 6 |
| `skills/visual-generation/SKILL.md` | skill | active | 184 | 6 |
| `.claude/commands/landing-status.md` | command-dot-claude | active | 135 | 6 |
| `commands/landing-status.md` | command-root | active | 135 | 6 |
| `.claude/commands/landing-clone.md` | command-dot-claude | active | 132 | 6 |
| `skills/landing-from-context/SKILL.md` | skill | active | 132 | 6 |
| `skills/prototype-import/SKILL.md` | skill | active | 122 | 6 |
| `skills/brand-kit-build/SKILL.md` | skill | active | 111 | 6 |
| `agents/icon-generator.md` | agent | active | 100 | 6 |
| `skills/style-decomposition/SKILL.md` | skill | active | 83 | 6 |
| `scripts/migrate-to-preview-panel.sh` | script | active | 37 | 6 |
| `skills/wp-gutenberg-block-builder/scripts/extract-main-css.py` | skill-script | active | 37 | 6 |
| `scripts/generate-wp-blocks.py.doc.md` | script-doc | doc-only | 12 | 6 |
| `scripts/gate-check.sh` | script | active | 649 | 5 |
| `skills/design-tokens-generation/SKILL.md` | skill | active | 296 | 5 |
| `scripts/preflight.sh` | script | active | 113 | 5 |
| `.claude/commands/landing-niche.md` | command-dot-claude | active | 103 | 5 |
| `commands/landing-niche.md` | command-root | active | 103 | 5 |
| `agents/system-setup.md` | agent | active | 82 | 5 |
| `skills/wireframe-rendering/scripts/render-wireframe.py` | skill-script | active | 37 | 5 |
| `skills/wp-multisite/scripts/clone-subsite.sh` | skill-script | active | 31 | 5 |
| `skills/wp-multisite/scripts/landing-segment.sh` | skill-script | active | 31 | 5 |
| `template/04_БРЕНД/logos/README.md` | template-readme | doc-only | 8 | 5 |
| `skills/block-library-management/SKILL.md` | skill | active | 834 | 4 |
| `skills/wp-cli-deployer/SKILL.md` | skill | active | 169 | 4 |
| `.claude/commands/landing-from-context.md` | command-dot-claude | active | 132 | 4 |
| `commands/landing-clone.md` | command-root | active | 132 | 4 |
| `commands/landing-from-context.md` | command-root | active | 132 | 4 |
| `agents/photo-matcher.md` | agent | active | 107 | 4 |
| `agents/photo-classifier.md` | agent | active | 103 | 4 |
| `.claude/commands/landing-setup.md` | command-dot-claude | active | 94 | 4 |
| `commands/landing-setup.md` | command-root | active | 94 | 4 |
| `agents/infographic-builder.md` | agent | active | 84 | 4 |
| `skills/landing-versioning-and-cloning/SKILL.md` | skill | active | 79 | 4 |
| `scripts/install-codex.sh` | script | active | 72 | 4 |
| `scripts/migrate-niche-to-v2.sh` | script | active | 43 | 4 |
| `scripts/verify-composed-has-visuals.sh` | script | active | 39 | 4 |
| `skills/visual-qa/scripts/visual-qa-loop.py` | skill-script | active | 35 | 4 |
| `scripts/import-blocks/import-from-url.sh` | script | active | 34 | 4 |
| `skills/style-decomposition/scripts/orchestrate.py` | skill-script | active | 32 | 4 |
| `skills/visual-qa/scripts/codex-review-screenshot.sh` | skill-script | active | 31 | 4 |
| `scripts/render-pipeline-map.sh.doc.md` | script-doc | doc-only | 9 | 4 |
| `skills/wp-builder/scripts/install_legal_pages.sh` | skill-script | active | 8 | 4 |
| `.claude/commands/landing-onboarding.md` | command-dot-claude | active | 318 | 3 |
| `commands/landing-onboarding.md` | command-root | active | 318 | 3 |
| `.claude/commands/landing-qa.md` | command-dot-claude | active | 190 | 3 |
| `commands/landing-qa.md` | command-root | active | 190 | 3 |
| `agents/photo-stylist.md` | agent | active | 124 | 3 |
| `skills/paralaximus-codex/SKILL.md` | skill | active | 90 | 3 |
| `skills/landing-project-init/scripts/init.sh` | skill-script | active | 89 | 3 |
| `skills/wp-theme-assembler/scripts/render-build-preview.py` | skill-script | active | 66 | 3 |
| `.claude/commands/landing-segment.md` | command-dot-claude | active | 63 | 3 |
| `skills/moodboard-creation/SKILL.md` | skill | active | 63 | 3 |
| `skills/client-assets-collection/SKILL.md` | skill | active | 59 | 3 |
| `skills/landing-versioning-and-cloning/scripts/clone-landing.sh` | skill-script | active | 56 | 3 |
| `skills/photo-curation/scripts/photo-pipeline.py` | skill-script | active | 55 | 3 |
| `scripts/export-palettes-to-library.py` | script | active | 52 | 3 |
| `skills/photo-curation/scripts/codex-process-photo.sh` | skill-script | active | 52 | 3 |
| `skills/wp-gutenberg-block-builder/scripts/generate-analytics.py` | skill-script | active | 49 | 3 |
| `skills/wp-gutenberg-block-builder/scripts/generate-integrations.py` | skill-script | active | 49 | 3 |
| `.claude/commands/landing-import-blocks.md` | command-dot-claude | active | 48 | 3 |
| `commands/landing-import-blocks.md` | command-root | active | 48 | 3 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php` | mu-plugin-php | active | 40 | 3 |
| `scripts/verify_visual_qa.py` | script | active | 38 | 3 |
| `scripts/backport-acf-to-legacy.sh` | script | active | 35 | 3 |
| `scripts/build-zip.sh` | script | active | 33 | 3 |
| `skills/wp-multisite/scripts/migrate-to-multisite.sh` | skill-script | active | 31 | 3 |
| `template/07a_WIREFRAME/README.md` | template-readme | doc-only | 28 | 3 |
| `template/07_ПРОТОТИП/README.md` | template-readme | doc-only | 24 | 3 |
| `template/07d_VISUALS/README.md` | template-readme | doc-only | 24 | 3 |
| `.claude/commands/landing-admin-install.md` | command-dot-claude | active | 23 | 3 |
| `template/04_БРЕНД/README.md` | template-readme | doc-only | 23 | 3 |
| `template/03_РЕФЕРЕНСЫ/README.md` | template-readme | doc-only | 20 | 3 |
| `template/08_КОД/README.md` | template-readme | doc-only | 20 | 3 |
| `template/09_ДЕПЛОЙ/README.md` | template-readme | doc-only | 20 | 3 |
| `skills/seo-tech-audit/SKILL.md` | skill | active | 17 | 3 |
| `.claude/commands/landing-audit.md` | command-dot-claude | active | 12 | 3 |
| `scripts/landing-final-check.sh.doc.md` | script-doc | doc-only | 8 | 3 |
| `scripts/landing-go-next-stage.py.doc.md` | script-doc | doc-only | 8 | 3 |
| `scripts/preflight.sh.doc.md` | script-doc | doc-only | 8 | 3 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/audit-runner.php` | mu-plugin-php | active | 7 | 3 |
| `template/07_ПРОТОТИП/source/README.md` | template-readme | doc-only | 4 | 3 |
| `docs/standards/stage-08-spec-lint.md` | standard | doc-only | 3 | 3 |
| `scripts/render-pipeline-map.sh` | script | active | 131 | 2 |
| `scripts/hooks/enforce_stage_gate.py` | script | active | 128 | 2 |
| `.claude/commands/landing-rollback.md` | command-dot-claude | active | 118 | 2 |
| `commands/landing-rollback.md` | command-root | active | 118 | 2 |
| `scripts/validate-all.sh` | script | active | 106 | 2 |
| `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` | skill-script | active | 94 | 2 |
| `.githooks/post-commit` | git-hook | active | 93 | 2 |
| `skills/block-composition/scripts/compose-blocks.py` | skill-script | active | 76 | 2 |
| `skills/photo-styling/SKILL.md` | skill | active | 69 | 2 |
| `skills/wp-theme-assembler/scripts/bundle-assets.py` | skill-script | active | 61 | 2 |
| `scripts/wizard-check-materials.py` | script | active | 60 | 2 |
| `skills/references-collection/SKILL.md` | skill | active | 58 | 2 |
| `config/positioning-modes.yaml` | config | active | 52 | 2 |
| `scripts/verify-visual-qa.sh` | script | active | 49 | 2 |
| `skills/wp-landing-config/scripts/install-mu-plugin.sh` | skill-script | active | 46 | 2 |
| `scripts/lib/stage_08_helper.py` | script | active | 43 | 2 |
| `skills/photo-curation/scripts/codex-classify.sh` | skill-script | active | 43 | 2 |
| `skills/photo-curation/scripts/codex-generate-fallback.sh` | skill-script | active | 43 | 2 |
| `skills/wp-gutenberg-block-builder/scripts/generate-js-init.py` | skill-script | active | 43 | 2 |
| `skills/wp-gutenberg-block-builder/scripts/generate-popup.py` | skill-script | active | 43 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php` | mu-plugin-php | active | 40 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php` | mu-plugin-php | active | 39 | 2 |
| `skills/photo-curation/scripts/codex-match.sh` | skill-script | active | 35 | 2 |
| `skills/paralaximus-codex/scripts/prepare-layers.py` | skill-script | active | 28 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/AmoCRMAdapter.php` | mu-plugin-php | active | 28 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/Bitrix24Adapter.php` | mu-plugin-php | active | 28 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/EmailAdapter.php` | mu-plugin-php | active | 28 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/HubSpotAdapter.php` | mu-plugin-php | active | 28 | 2 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/WhatsAppAdapter.php` | mu-plugin-php | active | 28 | 2 |
| `template/07b_COMPOSED/README.md` | template-readme | doc-only | 28 | 2 |
| `skills/moodboard-creation/scripts/scaffold.py` | skill-script | active | 21 | 2 |
| `template/07c_PHOTOS/README.md` | template-readme | doc-only | 20 | 2 |
| `scripts/_migrate-extract-palettes.py` | script | active | 12 | 2 |
| `scripts/block-loader.py.doc.md` | script-doc | doc-only | 12 | 2 |
| `scripts/gate-check.sh.doc.md` | script-doc | doc-only | 12 | 2 |
| `scripts/verify-composed-premium.sh.doc.md` | script-doc | doc-only | 12 | 2 |
| `scripts/verify-content-preserved.sh.doc.md` | script-doc | doc-only | 12 | 2 |
| `scripts/wiki/query.py.doc.md` | script-doc | doc-only | 12 | 2 |
| `scripts/checks/check_legal_blocks.sh` | script | active | 8 | 2 |
| `scripts/derive-landing-structure.py.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/gate-state.sh.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/lib/stage_08_helper.py.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/migrate-blocks-to-wireframe-format.py.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/migrate-niche-to-v2.sh.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/verify-visual-qa.sh.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/verify_visual_qa.py.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/wiki/cleanup_broken_links.py.doc.md` | script-doc | doc-only | 8 | 2 |
| `scripts/wiki/hooks/session_end.py.doc.md` | script-doc | doc-only | 8 | 2 |
| `template/07c_PHOTOS/inbox/до_после/README.md` | template-readme | doc-only | 4 | 2 |
| `template/07c_PHOTOS/inbox/документы_сертификаты/README.md` | template-readme | doc-only | 4 | 2 |
| `template/07c_PHOTOS/inbox/интерьер_экстерьер/README.md` | template-readme | doc-only | 4 | 2 |
| `template/07c_PHOTOS/inbox/объекты_и_продукты/README.md` | template-readme | doc-only | 4 | 2 |
| `template/07c_PHOTOS/inbox/портреты_и_команда/README.md` | template-readme | doc-only | 4 | 2 |
| `template/07c_PHOTOS/inbox/процесс_работы/README.md` | template-readme | doc-only | 4 | 2 |
| `template/13_СЕГМЕНТЫ_ЦА/_skeleton/README.md` | template-readme | doc-only | 4 | 2 |
| `scripts/gate-state.sh` | script | active | 193 | 1 |
| `scripts/verify-composed-premium.sh` | script | active | 102 | 1 |
| `skills/legal-pages-render/scripts/render.py` | skill-script | active | 85 | 1 |
| `skills/moodboard-creation/scripts/render.py` | skill-script | active | 84 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py` | skill-script | active | 73 | 1 |
| `skills/paralaximus-codex/scripts/generate-atlas.sh` | skill-script | active | 70 | 1 |
| `config/niche-visual-rules.yaml` | config | active | 67 | 1 |
| `scripts/verify-content-preserved.sh` | script | active | 66 | 1 |
| `skills/photo-styling/scripts/style.py` | skill-script | active | 66 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py` | skill-script | active | 65 | 1 |
| `scripts/check-wiki-sync.sh` | script | active | 64 | 1 |
| `skills/style-decomposition/scripts/identify-fonts.py` | skill-script | active | 63 | 1 |
| `skills/design-tokens-generation/scripts/render-preview.py` | skill-script | active | 61 | 1 |
| `scripts/verify-photo-pipeline.sh` | script | active | 58 | 1 |
| `scripts/wiki/query.py` | script | doc-only | 56 | 1 |
| `skills/visual-generation/scripts/codex-generate-icon.sh` | skill-script | active | 56 | 1 |
| `.claude/commands/landing-final-check.md` | command-dot-claude | active | 55 | 1 |
| `commands/landing-final-check.md` | command-root | active | 55 | 1 |
| `skills/niche-analysis/scripts/validate-landing-structure.py` | skill-script | active | 53 | 1 |
| `skills/niche-analysis/scripts/validate-positioning.py` | skill-script | active | 53 | 1 |
| `scripts/wiki/config.py` | script | active | 51 | 1 |
| `skills/visual-qa/scripts/apply-fix.py` | skill-script | active | 50 | 1 |
| `scripts/derive-landing-structure.py` | script | active | 47 | 1 |
| `skills/visual-generation/scripts/slot-scanner.py` | skill-script | active | 44 | 1 |
| `scripts/snapshot-palettes-to-project.py` | script | active | 40 | 1 |
| `skills/landing-versioning-and-cloning/scripts/create-version.sh` | skill-script | active | 40 | 1 |
| `block-library/hero/ru-hero-08-centered-emailcap/meta.yaml` | block-meta | active | 39 | 1 |
| `scripts/wiki/hooks/pre_compact.py` | script | doc-only | 36 | 1 |
| `scripts/wiki/hooks/session_end.py` | script | doc-only | 36 | 1 |
| `scripts/mark-legacy-projects.sh` | script | active | 35 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/check-block-php-markers.py` | skill-script | active | 35 | 1 |
| `scripts/wiki/system_compiler.py` | script | doc-only | 33 | 1 |
| `skills/style-decomposition/scripts/download-fonts.py` | skill-script | active | 32 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php` | mu-plugin-php | active | 32 | 1 |
| `.claude/commands/landing-previews.md` | command-dot-claude | active | 31 | 1 |
| `commands/landing-previews.md` | command-root | active | 31 | 1 |
| `template/memory/README.md` | template-readme | doc-only | 28 | 1 |
| `template/wiki/README.md` | template-readme | doc-only | 28 | 1 |
| `scripts/block-loader.py` | script | active | 24 | 1 |
| `skills/photo-curation/scripts/preview-render.py` | skill-script | active | 24 | 1 |
| `template/10_QA/README.md` | template-readme | doc-only | 24 | 1 |
| `template/12_SEO/README.md` | template-readme | doc-only | 24 | 1 |
| `block-library/contacts/contacts-brutalist-split-antidiler-karpov-ru-7/meta.yaml` | block-meta | doc-only | 23 | 1 |
| `block-library/cta/cta-brutalist-split-sskrusgun-ru-3/meta.yaml` | block-meta | doc-only | 23 | 1 |
| `block-library/cta/cta-brutalist-split-sskrusgun-ru-9/meta.yaml` | block-meta | doc-only | 23 | 1 |
| `block-library/features/features-brutalist-grid-3-portfolio-kdm1-ru-3/meta.yaml` | block-meta | doc-only | 23 | 1 |
| `block-library/features/features-brutalist-split-antidiler-karpov-ru-2/meta.yaml` | block-meta | doc-only | 23 | 1 |
| `block-library/hero/hero-brutalist-split-sskrusgun-ru-1/meta.yaml` | block-meta | doc-only | 23 | 1 |
| `skills/paralaximus-codex/scripts/remove-bg.sh` | skill-script | active | 22 | 1 |
| `scripts/wiki/cleanup_broken_links.py` | script | doc-only | 20 | 1 |
| `template/00_БРИФ/README.md` | template-readme | doc-only | 20 | 1 |
| `template/01_КОНТЕКСТ/README.md` | template-readme | doc-only | 20 | 1 |
| `template/02_МАТЕРИАЛЫ_КЛИЕНТА/README.md` | template-readme | doc-only | 20 | 1 |
| `template/05_ДИЗАЙН-СИСТЕМА/README.md` | template-readme | doc-only | 20 | 1 |
| `template/06_СТЕК/README.md` | template-readme | doc-only | 20 | 1 |
| `template/07_КОНТЕНТ/README.md` | template-readme | doc-only | 20 | 1 |
| `template/11_АНАЛИТИКА/README.md` | template-readme | doc-only | 20 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/check-section5-css.py` | skill-script | active | 19 | 1 |
| `skills/seo-tech-audit/scripts/run-audit.py` | skill-script | active | 18 | 1 |
| `scripts/migrate-blocks-to-wireframe-format.py` | script | doc-only | 16 | 1 |
| `skills/photo-curation/scripts/classify-photos.py` | skill-script | active | 15 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/render.php` | mu-plugin-php | active | 15 | 1 |
| `scripts/build-zip.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/generate-palette-css.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/import-blocks/codex-analyze-structure.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/import-blocks/generate-blocks.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/import-blocks/import-from-url.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/import-blocks/take-page-screenshot.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/import-blocks/update-catalog.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/install-git-hooks.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/mark-legacy-projects.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/migrate-add-wiki.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/migrate-template-readmes.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/setup-flag.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/validate-all.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/validate-palettes.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/verify-composed-has-visuals.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/verify-identity-preserved.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/verify-php-syntax.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/conversations_compiler.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/hash_cache.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/lint.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/parsers/composed_html.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/parsers/tokens_json.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/project_graph_compiler.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wiki/system_compiler.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wizard-check-materials.py.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/wizard.sh.doc.md` | script-doc | doc-only | 12 | 1 |
| `scripts/generate-script-docs.py` | script | active | 11 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config-loader.php` | mu-plugin-php | active | 11 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/resolver.php` | mu-plugin-php | active | 11 | 1 |
| `scripts/backport-acf-to-legacy.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/check-deps.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/check-wiki-sync.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/deploy.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/export-palettes-to-library.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/extract-effects/build-patterns-library.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/extract-effects/extract-patterns.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/extract-effects/scrape-css.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/generate-axes-filter.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/generate-previews.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/install-codex.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/lib/check-block-registration.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/lib/content_parser.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/migrate-state-add-01a.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/migrate-state-for-prd.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/migrate-to-preview-panel.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/preview-blocks-library.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/refresh-catalog.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/snapshot-palettes-to-project.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/test-pipeline.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/verify-gutenberg-json.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/verify-photo-pipeline.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/verify-site-url.sh.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/verify_content_preserved.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/verify_photo_pipeline.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/compile.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/config.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/flush.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/hooks/pre_compact.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/hooks/session_start.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/parsers/selections_yaml.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/parsers/state_yaml.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/preview.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/sdk_client.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `scripts/wiki/utils.py.doc.md` | script-doc | doc-only | 8 | 1 |
| `skills/wp-cli-deployer/scripts/fix-page-content-images.py` | skill-script | active | 8 | 1 |
| `skills/photo-curation/scripts/match-photos-to-slots.py` | skill-script | active | 7 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-network.php` | mu-plugin-php | active | 7 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/admin-network.php` | mu-plugin-php | active | 7 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py` | skill-script | doc-only | 6 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php` | mu-plugin-php | active | 6 | 1 |
| `scripts/sync-commands.sh` | script | active | 5 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/enqueue.php` | mu-plugin-php | active | 5 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/lib/lint_heuristics.py` | skill-script | active | 4 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/bottom-bar.php` | mu-plugin-php | active | 4 | 1 |
| `template/13_СЕГМЕНТЫ_ЦА/README.md` | template-readme | doc-only | 4 | 1 |
| `skills/wp-gutenberg-block-builder/scripts/lib/composed_inspector.py` | skill-script | doc-only | 3 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/center-modal.php` | mu-plugin-php | doc-only | 2 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/floating-card-left.php` | mu-plugin-php | doc-only | 2 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/floating-card-right.php` | mu-plugin-php | doc-only | 2 | 1 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/top-bar.php` | mu-plugin-php | doc-only | 2 | 1 |
| `scripts/setup-flag.sh` | script | active | 220 | 0 |
| `block-library/_styles/brutalist/style-guide.md` | style-guide | active | 214 | 0 |
| `skills/wp-multisite/scripts/lib/state.sh` | skill-script | active | 214 | 0 |
| `scripts/wiki/preview.py` | script | active | 153 | 0 |
| `scripts/wiki/compile.py` | script | active | 113 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cascade.php` | mu-plugin-php | active | 104 | 0 |
| `block-library/hero/ru-hero-01-services-calc/meta.yaml` | block-meta | active | 103 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` | mu-plugin-php | active | 92 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cta.php` | mu-plugin-php | active | 91 | 0 |
| `skills/block-composition/scripts/inject-content.py` | skill-script | active | 88 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/integrations.php` | mu-plugin-php | active | 84 | 0 |
| `skills/niche-analysis/scripts/validate-competitors.py` | skill-script | active | 79 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/helpers.php` | mu-plugin-php | active | 76 | 0 |
| `skills/block-composition/scripts/inject-tokens.py` | skill-script | active | 75 | 0 |
| `docs/standards/premium-07b-checklist.md` | standard | active | 74 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/encryption.php` | mu-plugin-php | active | 73 | 0 |
| `skills/gpt5-prompting-engine/SKILL.md` | skill | active | 72 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php` | mu-plugin-php | active | 72 | 0 |
| `skills/wp-gutenberg-block-builder/scripts/generate-page-content.py` | skill-script | active | 71 | 0 |
| `scripts/check-deps.sh` | script | active | 70 | 0 |
| `skills/design-tokens-generation/scripts/build-tokens.py` | skill-script | active | 67 | 0 |
| `skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py` | skill-script | active | 64 | 0 |
| `block-library/features/ru-features-01-3col-icons/meta.yaml` | block-meta | active | 63 | 0 |
| `scripts/wiki/flush.py` | script | active | 63 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php` | mu-plugin-php | active | 60 | 0 |
| `scripts/verify-identity-preserved.sh` | script | active | 59 | 0 |
| `scripts/wiki/__init__.py` | script | doc-only | 58 | 0 |
| `scripts/wiki/hooks/__init__.py` | script | doc-only | 58 | 0 |
| `scripts/wiki/parsers/__init__.py` | script | doc-only | 58 | 0 |
| `scripts/wiki/prompts/__init__.py` | script | doc-only | 58 | 0 |
| `skills/photo-curation/scripts/__init__.py` | skill-script | doc-only | 58 | 0 |
| `skills/seo-tech-audit/scripts/lib/__init__.py` | skill-script | doc-only | 58 | 0 |
| `skills/seo-tech-audit/scripts/runners/__init__.py` | skill-script | doc-only | 58 | 0 |
| `skills/visual-generation/scripts/__init__.py` | skill-script | doc-only | 58 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` | mu-plugin-php | active | 58 | 0 |
| `skills/style-decomposition/scripts/extract-palette.py` | skill-script | active | 57 | 0 |
| `skills/style-decomposition/scripts/match-icons.py` | skill-script | active | 57 | 0 |
| `block-library/features/ru-features-02-bento-grid/meta.yaml` | block-meta | active | 55 | 0 |
| `block-library/quiz/ru-quiz-01-step-card/meta.yaml` | block-meta | active | 55 | 0 |
| `scripts/wiki/lint.py` | script | doc-only | 55 | 0 |
| `skills/niche-analysis/scripts/validate-visual-requirements.py` | skill-script | active | 55 | 0 |
| `scripts/lib/content_parser.py` | script | active | 53 | 0 |
| `skills/niche-analysis/scripts/validate-market-profile.py` | skill-script | active | 53 | 0 |
| `skills/photo-curation/scripts/render-prompt.py` | skill-script | active | 52 | 0 |
| `skills/prototype-import/scripts/validate-prototype.py` | skill-script | active | 52 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-statuses.php` | mu-plugin-php | active | 52 | 0 |
| `block-library/cta/ru-cta-01-callback-tg-max/meta.yaml` | block-meta | active | 51 | 0 |
| `block-library/hero/ru-hero-02-b2c-expert/meta.yaml` | block-meta | active | 51 | 0 |
| `block-library/hero/ru-hero-03-local-interior/meta.yaml` | block-meta | active | 51 | 0 |
| `block-library/pricing/ru-pricing-01-rub-from/meta.yaml` | block-meta | active | 51 | 0 |
| `block-library/quiz/ru-quiz-05-thankyou/meta.yaml` | block-meta | active | 51 | 0 |
| `block-library/trust/ru-trust-01-guarantees-docs/meta.yaml` | block-meta | active | 51 | 0 |
| `scripts/validate-palettes.py` | script | active | 51 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php` | mu-plugin-php | active | 50 | 0 |
| `scripts/generate-axes-filter.py` | script | active | 49 | 0 |
| `scripts/generate-palette-css.py` | script | active | 49 | 0 |
| `skills/photo-curation/scripts/identity-check.py` | skill-script | active | 48 | 0 |
| `skills/visual-generation/scripts/prompt-picker.py` | skill-script | doc-only | 48 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php` | mu-plugin-php | active | 48 | 0 |
| `block-library/faq/ru-faq-01-accordion/meta.yaml` | block-meta | active | 47 | 0 |
| `block-library/process/ru-process-01-4steps-icons/meta.yaml` | block-meta | active | 47 | 0 |
| `block-library/quiz/ru-quiz-02-progress-top/meta.yaml` | block-meta | active | 47 | 0 |
| `block-library/quiz/ru-quiz-03-intermediate/meta.yaml` | block-meta | active | 47 | 0 |
| `block-library/quiz/ru-quiz-04-lead-form/meta.yaml` | block-meta | active | 47 | 0 |
| `block-library/social-proof/ru-testimonials-01-video-circles/meta.yaml` | block-meta | active | 47 | 0 |
| `block-library/social-proof/ru-testimonials-02-text-photo/meta.yaml` | block-meta | active | 47 | 0 |
| `scripts/verify_content_preserved.py` | script | active | 47 | 0 |
| `skills/photo-curation/scripts/selections-validator.py` | skill-script | active | 47 | 0 |
| `skills/brand-kit-build/scripts/build.py` | skill-script | active | 45 | 0 |
| `skills/client-assets-collection/scripts/parse-reviews.py` | skill-script | active | 44 | 0 |
| `skills/references-collection/scripts/index.py` | skill-script | active | 44 | 0 |
| `block-library/cta/ru-cta-06-editorial-paper/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/cta/ru-cta-07-accent-bg/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/features/ru-features-03-swiss-cards/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/hero/ru-hero-04-split-form/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/hero/ru-hero-07-editorial-serif/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/hero/ru-hero-10-deck-cover/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/quiz/ru-quiz-06-welcome-screen/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/quiz/ru-quiz-07-image-choice/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/quiz/ru-quiz-09-multi-select/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/quiz/ru-quiz-10-loader-analyzing/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/quiz/ru-quiz-11-discount-bonus/meta.yaml` | block-meta | active | 43 | 0 |
| `block-library/quiz/ru-quiz-13-comparison-question/meta.yaml` | block-meta | active | 43 | 0 |
| `scripts/install-git-hooks.sh` | script | doc-only | 43 | 0 |
| `scripts/migrate-add-wiki.sh` | script | active | 43 | 0 |
| `scripts/wiki/utils.py` | script | active | 43 | 0 |
| `skills/block-library-management/scripts/scaffold-block.py` | skill-script | active | 43 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php` | mu-plugin-php | active | 43 | 0 |
| `skills/photo-curation/scripts/svg-placeholder.py` | skill-script | active | 41 | 0 |
| `skills/brand-kit-build/scripts/render-html.py` | skill-script | active | 40 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/network.php` | mu-plugin-php | active | 40 | 0 |
| `block-library/cta/ru-cta-02-banner-stripe/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/cta/ru-cta-03-urgency-scarcity/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/cta/ru-cta-04-lead-magnet/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/cta/ru-cta-05-login-cta/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/faq/ru-faq-02-why-us/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/faq/ru-faq-03-searchable/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/faq/ru-faq-04-pricing-faq/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/features/ru-features-04-numbered-list/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/features/ru-features-05-method-steps/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/features/ru-features-06-cards-2x2/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/features/ru-features-07-2col-split/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/hero/ru-hero-05-centered-bold/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/hero/ru-hero-06-swiss-metrics/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/hero/ru-hero-09-kami-serif/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/pricing/ru-pricing-02-comparison-table/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/pricing/ru-pricing-03-3tier-saas/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/pricing/ru-pricing-04-tiers-faq/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/process/ru-process-02-next-steps/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/process/ru-process-03-4steps-numbered/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/quiz/ru-quiz-08-slider-range/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/quiz/ru-quiz-12-mini-calculator/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-social-proof-03-client-logos/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-social-proof-04-authority-cases/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-social-proof-05-metrics-editorial/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-social-proof-06-editorial-quote/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-social-proof-07-logo-ticker/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-social-proof-08-stats-deck/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/social-proof/ru-stats-01-growth-chart/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/trust/ru-trust-02-numbers-row/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/trust/ru-trust-03-descriptor-header/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/trust/ru-trust-04-principles-grid/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/trust/ru-trust-05-manifesto-text/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/trust/ru-trust-06-labs-showcase/meta.yaml` | block-meta | active | 39 | 0 |
| `block-library/trust/ru-trust-07-partner-logos/meta.yaml` | block-meta | active | 39 | 0 |
| `scripts/landing-go-next-stage.py` | script | active | 39 | 0 |
| `scripts/migrate-state-for-prd.sh` | script | active | 39 | 0 |
| `scripts/migrate-template-readmes.sh` | script | active | 39 | 0 |
| `scripts/verify-gutenberg-json.sh` | script | active | 39 | 0 |
| `scripts/verify-php-syntax.sh` | script | active | 39 | 0 |
| `scripts/verify-site-url.sh` | script | active | 39 | 0 |
| `scripts/verify_photo_pipeline.py` | script | active | 39 | 0 |
| `skills/block-composition/scripts/validate-selections.py` | skill-script | active | 39 | 0 |
| `block-library/_styles/editorial-warm/style-guide.md` | style-guide | active | 37 | 0 |
| `scripts/wiki/hooks/session_start.py` | script | doc-only | 36 | 0 |
| `skills/photo-curation/scripts/intake.py` | skill-script | active | 36 | 0 |
| `skills/visual-generation/scripts/visual-cache.py` | skill-script | active | 36 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-status-log.php` | mu-plugin-php | active | 36 | 0 |
| `block-library/features/ru-features-08-kpi-metrics/meta.yaml` | block-meta | active | 35 | 0 |
| `scripts/migrate-state-add-01a.sh` | script | active | 35 | 0 |
| `skills/client-assets-collection/scripts/collect.py` | skill-script | active | 35 | 0 |
| `skills/prototype-import/scripts/extract-pdf-text.py` | skill-script | active | 35 | 0 |
| `skills/prototype-import/scripts/md-to-yaml.py` | skill-script | active | 35 | 0 |
| `skills/visual-qa/scripts/take-screenshots.py` | skill-script | active | 35 | 0 |
| `skills/photo-curation/scripts/gallery-render.py` | skill-script | active | 32 | 0 |
| `skills/wp-multisite/scripts/lib/beget-api.sh` | skill-script | active | 32 | 0 |
| `scripts/wiki/project_graph_compiler.py` | script | active | 31 | 0 |
| `skills/block-library-management/scripts/validate-catalog.py` | skill-script | active | 31 | 0 |
| `skills/block-library-management/scripts/validate-meta.py` | skill-script | active | 31 | 0 |
| `skills/photo-curation/scripts/call-codex.sh` | skill-script | active | 31 | 0 |
| `skills/visual-generation/scripts/codex-generate-infographic.sh` | skill-script | active | 31 | 0 |
| `block-library/_patterns/glass-00/meta.yaml` | pattern-meta | doc-only | 27 | 0 |
| `block-library/_patterns/glass-01/meta.yaml` | pattern-meta | doc-only | 27 | 0 |
| `block-library/hero/hero-cinematic-split-antidiler-karpov-ru-1/meta.yaml` | block-meta | active | 27 | 0 |
| `scripts/extract-effects/build-patterns-library.py` | script | active | 27 | 0 |
| `scripts/extract-effects/extract-patterns.py` | script | active | 27 | 0 |
| `scripts/generate-previews.sh` | script | active | 27 | 0 |
| `scripts/wiki/conversations_compiler.py` | script | active | 27 | 0 |
| `scripts/wiki/sdk_client.py` | script | doc-only | 27 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php` | mu-plugin-php | active | 27 | 0 |
| `scripts/lib/check-block-registration.sh` | script | doc-only | 26 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/schema.php` | mu-plugin-php | active | 25 | 0 |
| `block-library/_styles/retro-windows/style-guide.md` | style-guide | active | 24 | 0 |
| `scripts/wiki/hash_cache.py` | script | doc-only | 24 | 0 |
| `scripts/wiki/parsers/composed_html.py` | script | doc-only | 24 | 0 |
| `skills/visual-generation/scripts/lucide-fetcher.py` | skill-script | doc-only | 24 | 0 |
| `skills/wireframe-rendering/scripts/serve-preview.sh` | skill-script | active | 24 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-readonly.php` | mu-plugin-php | active | 24 | 0 |
| `block-library/contacts/contacts-corporate-grid-2-opt-ecowash-ru-11/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/contacts/contacts-corporate-split-medregistrant-ru-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/contacts/contacts-corporate-split-portfolio-kdm1-ru-16/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-cinematic-split-portfolio-kdm1-ru-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-cinematic-split-portfolio-kdm1-ru-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-corporate-centered-portfolio-kdm1-ru-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-corporate-centered-zilant-group-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-corporate-grid-3-medregistrant-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-corporate-split-project21993216-tild-13/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-corporate-split-project21993216-tild-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-corporate-stacked-romanmelnikov-tilda-13/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-minimal-centered-opt-ecowash-ru-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-minimal-split-portfolio-kdm1-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-minimal-split-project21993216-tild-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-technical-centered-antidiler-karpov-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/cta/cta-technical-split-medregistrant-ru-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/faq/faq-corporate-stacked-portfolio-kdm1-ru-15/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/faq/faq-minimal-stacked-project21993216-tild-11/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/faq/faq-minimal-stacked-sskrusgun-ru-13/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-cinematic-stacked-portfolio-kdm1-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-corporate-grid-2-portfolio-kdm1-ru-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-corporate-grid-3-opt-ecowash-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-corporate-split-romanmelnikov-tilda-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-corporate-split-sskrusgun-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-editorial-cards-romanmelnikov-tilda-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-editorial-grid-2-romanmelnikov-tilda-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-editorial-split-project21993216-tild-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-editorial-stacked-romanmelnikov-tilda-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-minimal-centered-opt-ecowash-ru-10/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-minimal-grid-2-sskrusgun-ru-10/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-minimal-grid-2-sskrusgun-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-minimal-grid-2-zilant-group-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-minimal-grid-4-zilant-group-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-playful-cards-opt-ecowash-ru-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-playful-centered-medregistrant-ru-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-centered-medregistrant-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-centered-portfolio-kdm1-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-2-portfolio-kdm1-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-2-romanmelnikov-tilda-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-3-portfolio-kdm1-ru-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-3-portfolio-kdm1-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-3-portfolio-kdm1-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-3-zilant-group-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-grid-4-project21993216-tild-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/features/features-technical-split-sskrusgun-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-corporate-grid-3-sskrusgun-ru-14/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-corporate-grid-4-portfolio-kdm1-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-corporate-grid-4-zilant-group-10/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-corporate-split-opt-ecowash-ru-12/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-corporate-split-portfolio-kdm1-ru-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-minimal-grid-3-project21993216-tild-14/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-minimal-split-antidiler-karpov-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-minimal-split-portfolio-kdm1-ru-17/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/footer/footer-minimal-split-romanmelnikov-tilda-14/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-cinematic-cards-zilant-group-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-cinematic-grid-4-sskrusgun-ru-12/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-corporate-cards-portfolio-kdm1-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-editorial-grid-3-portfolio-kdm1-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-minimal-grid-3-project21993216-tild-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-minimal-stacked-portfolio-kdm1-ru-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/gallery/gallery-playful-grid-4-project21993216-tild-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-cinematic-split-antidiler-karpov-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-cinematic-split-portfolio-kdm1-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-corporate-split-portfolio-kdm1-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-corporate-split-zilant-group-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-luxury-split-romanmelnikov-tilda-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-minimal-split-medregistrant-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-minimal-split-portfolio-kdm1-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-minimal-split-project21993216-tild-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-playful-split-opt-ecowash-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/header/header-technical-split-sskrusgun-ru-0/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-cinematic-centered-portfolio-kdm1-ru-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-cinematic-split-portfolio-kdm1-ru-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-cinematic-split-romanmelnikov-tilda-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-corporate-split-project21993216-tild-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-corporate-split-zilant-group-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-editorial-centered-medregistrant-ru-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-minimal-split-portfolio-kdm1-ru-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-playful-split-opt-ecowash-ru-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/hero/hero-technical-split-portfolio-kdm1-ru-1/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-corporate-cards-opt-ecowash-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-corporate-grid-2-portfolio-kdm1-ru-10/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-corporate-grid-3-portfolio-kdm1-ru-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-corporate-grid-3-sskrusgun-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-luxury-split-romanmelnikov-tilda-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-minimal-grid-4-sskrusgun-ru-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/pricing/pricing-technical-grid-3-sskrusgun-ru-2/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-cinematic-timeline-portfolio-kdm1-ru-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-corporate-stacked-portfolio-kdm1-ru-13/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-corporate-timeline-project21993216-tild-10/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-editorial-grid-2-romanmelnikov-tilda-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-minimal-grid-2-opt-ecowash-ru-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-minimal-grid-2-portfolio-kdm1-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-technical-cards-medregistrant-ru-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-technical-stacked-opt-ecowash-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/process/process-technical-timeline-romanmelnikov-tilda-10/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-cinematic-split-antidiler-karpov-ru-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-corporate-cards-medregistrant-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-corporate-grid-3-zilant-group-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-luxury-cards-romanmelnikov-tilda-12/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-minimal-centered-project21993216-tild-3/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-minimal-stacked-antidiler-karpov-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-playful-grid-2-opt-ecowash-ru-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/social-proof/social-proof-technical-grid-4-portfolio-kdm1-ru-14/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/team/team-cinematic-split-portfolio-kdm1-ru-11/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-corporate-grid-2-portfolio-kdm1-ru-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-corporate-grid-3-project21993216-tild-12/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-corporate-grid-4-sskrusgun-ru-11/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-editorial-grid-2-romanmelnikov-tilda-11/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-editorial-grid-2-zilant-group-7/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-editorial-grid-3-portfolio-kdm1-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-editorial-stacked-medregistrant-ru-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-editorial-stacked-portfolio-kdm1-ru-12/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-luxury-centered-romanmelnikov-tilda-5/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-minimal-centered-antidiler-karpov-ru-6/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-minimal-grid-4-zilant-group-8/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-playful-stacked-opt-ecowash-ru-4/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `block-library/trust/trust-technical-grid-3-project21993216-tild-9/meta.yaml` | block-meta | doc-only | 23 | 0 |
| `scripts/extract-effects/scrape-css.sh` | script | active | 23 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/segment-selector.php` | mu-plugin-php | active | 21 | 0 |
| `scripts/import-blocks/codex-analyze-structure.sh` | script | active | 20 | 0 |
| `scripts/import-blocks/generate-blocks.py` | script | active | 20 | 0 |
| `scripts/import-blocks/take-page-screenshot.py` | script | active | 20 | 0 |
| `scripts/import-blocks/update-catalog.py` | script | active | 20 | 0 |
| `scripts/wiki/parsers/selections_yaml.py` | script | doc-only | 20 | 0 |
| `scripts/wiki/parsers/state_yaml.py` | script | doc-only | 20 | 0 |
| `scripts/wiki/parsers/tokens_json.py` | script | doc-only | 20 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta-readonly.php` | mu-plugin-php | active | 20 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations-readonly.php` | mu-plugin-php | active | 20 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php` | mu-plugin-php | active | 20 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php` | mu-plugin-php | active | 20 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php` | mu-plugin-php | active | 20 | 0 |
| `skills/wp-multisite/scripts/lib/ssh-helpers.sh` | skill-script | active | 20 | 0 |
| `block-library/_patterns/animation-00-button-icon-fade-in/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-01-checkicondraw/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-02-checkiconopacity/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-03-checkiconscale/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-04-fade-in/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-05-fade-out/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-06-fadeout/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-07-iconbackgroundopacity/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-08-iconbackgroundtransform/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/animation-09-move-down/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-00-item-0/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-01-item-1/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-02-item-2/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-03-item-3/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-04-item-4/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-05-item-5/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-06-item-6/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-07-item-7/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-08-item-8/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `block-library/_patterns/hover-effect-09-item-9/meta.yaml` | pattern-meta | doc-only | 19 | 0 |
| `scripts/preview-blocks-library.py` | script | active | 19 | 0 |
| `skills/wireframe-rendering/scripts/enrich-quiz-funnel.py` | skill-script | active | 18 | 0 |
| `block-library/_styles/coral-soft/style-guide.md` | style-guide | active | 17 | 0 |
| `block-library/_styles/monochrome-precision/style-guide.md` | style-guide | active | 17 | 0 |
| `block-library/_styles/swiss-modernist/style-guide.md` | style-guide | active | 17 | 0 |
| `scripts/refresh-catalog.py` | script | doc-only | 16 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads-network.php` | mu-plugin-php | active | 16 | 0 |
| `skills/photo-curation/scripts/detect-region.py` | skill-script | active | 15 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/cpt.php` | mu-plugin-php | active | 15 | 0 |
| `skills/wp-landing-config/scripts/test-smoke-rest.sh` | skill-script | active | 15 | 0 |
| `scripts/_migrate-strip-header.py` | script | active | 12 | 0 |
| `scripts/_migrate-strip-js.py` | script | active | 12 | 0 |
| `skills/seo-tech-audit/scripts/runners/ai_readiness.py` | skill-script | doc-only | 10 | 0 |
| `skills/brand-kit-build/scripts/parse_legal.py` | skill-script | active | 9 | 0 |
| `skills/seo-tech-audit/scripts/runners/html_checks.py` | skill-script | doc-only | 9 | 0 |
| `skills/seo-tech-audit/scripts/runners/network_checks.py` | skill-script | doc-only | 9 | 0 |
| `skills/seo-tech-audit/scripts/runners/schema_checks.py` | skill-script | doc-only | 9 | 0 |
| `skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py` | skill-script | doc-only | 9 | 0 |
| `skills/wp-gutenberg-block-builder/scripts/lib/design_extractor.py` | skill-script | active | 8 | 0 |
| `skills/block-library-management/scripts/render-gallery.py` | skill-script | active | 7 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/migrate.php` | mu-plugin-php | active | 7 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/deep-links.php` | mu-plugin-php | active | 7 | 0 |
| `skills/seo-tech-audit/scripts/lib/report.py` | skill-script | doc-only | 6 | 0 |
| `skills/seo-tech-audit/scripts/lib/http_client.py` | skill-script | doc-only | 5 | 0 |
| `skills/seo-tech-audit/scripts/lib/thresholds.py` | skill-script | doc-only | 5 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-site-readonly.php` | mu-plugin-php | active | 5 | 0 |
| `skills/wp-gutenberg-block-builder/scripts/lib/control_types.py` | skill-script | doc-only | 4 | 0 |
| `skills/wp-gutenberg-block-builder/scripts/lib/spec_inspector.py` | skill-script | doc-only | 4 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/llms-txt-rewrite.php` | mu-plugin-php | active | 3 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/html.php` | mu-plugin-php | doc-only | 3 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/overview.php` | mu-plugin-php | doc-only | 3 | 0 |
| `skills/seo-tech-audit/scripts/lib/fix_actions.py` | skill-script | doc-only | 2 | 0 |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/ai_readiness.php` | mu-plugin-php | doc-only | 2 | 0 |
| `skills/seo-tech-audit/scripts/lib/site_discovery.py` | skill-script | doc-only | 1 | 0 |

## Расхождение `.claude/commands/` vs `commands/`

| Команда | В `.claude/commands/` | В `commands/` | Размеры (.claude / commands) | Размеры совпадают | Контент идентичен |
|---|:---:|:---:|---|:---:|:---:|
| `landing-admin-install` | да | нет | — | — | — |
| `landing-audit` | да | нет | — | — | — |
| `landing-brand` | да | да | 1610 / 1610 | да | да |
| `landing-build` | да | да | 5302 / 5302 | да | да |
| `landing-clone` | да | да | 2320 / 423 | нет | нет |
| `landing-compose` | да | да | 1168 / 1168 | да | да |
| `landing-content` | да | да | 1760 / 1760 | да | да |
| `landing-deploy` | да | да | 1350 / 1350 | да | да |
| `landing-design` | да | да | 2061 / 2061 | да | да |
| `landing-final-check` | да | да | 906 / 906 | да | да |
| `landing-from-context` | да | да | 1291 / 1291 | да | да |
| `landing-go` | да | да | 4975 / 4975 | да | да |
| `landing-help` | да | да | 1475 / 1475 | да | да |
| `landing-import-blocks` | да | да | 2253 / 2253 | да | да |
| `landing-moodboard` | да | да | 1496 / 1496 | да | да |
| `landing-new` | да | да | 1816 / 1816 | да | да |
| `landing-niche` | да | да | 1687 / 1687 | да | да |
| `landing-onboarding` | да | да | 645 / 645 | да | да |
| `landing-photos` | да | да | 5658 / 5658 | да | да |
| `landing-previews` | да | да | 719 / 719 | да | да |
| `landing-prototype` | да | да | 1763 / 1763 | да | да |
| `landing-qa` | да | да | 2065 / 2065 | да | да |
| `landing-references` | да | да | 1623 / 1623 | да | да |
| `landing-rollback` | да | да | 439 / 439 | да | да |
| `landing-segment` | да | нет | — | — | — |
| `landing-setup` | да | да | 1016 / 1016 | да | да |
| `landing-stack` | да | да | 1695 / 1695 | да | да |
| `landing-start` | да | да | 2994 / 2994 | да | да |
| `landing-status` | да | да | 3213 / 3213 | да | да |
| `landing-style` | да | да | 5560 / 5560 | да | да |
| `landing-visuals` | да | да | 3415 / 3415 | да | да |
| `landing-wireframe` | да | да | 1346 / 1346 | да | да |

**Итого расхождений** (отсутствует в одной папке либо содержимое не совпадает): **4**.

## Кластеры по префиксу имени

Группировка файлов по первому токену имени (часть до первого `-` или `_`). Показаны кластеры с ≥2 файлами. Кластеры из `block-library/*/` и `block-library/_patterns/` исключены — они содержат сотни однотипных мета-файлов и не несут диагностической ценности на этом уровне.

### Кластер `README-*` (33 файлов)

- `template/00_БРИФ/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/01_КОНТЕКСТ/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/01a_АНАЛИЗ_НИШИ/README.md` — template-readme, doc-only, вход. ссылок: 56
- `template/02_МАТЕРИАЛЫ_КЛИЕНТА/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/03_РЕФЕРЕНСЫ/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/04_БРЕНД/README.md` — template-readme, doc-only, вход. ссылок: 23
- `template/04_БРЕНД/logos/README.md` — template-readme, doc-only, вход. ссылок: 8
- `template/05_ДИЗАЙН-СИСТЕМА/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/06_СТЕК/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/07_КОНТЕНТ/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/07_ПРОТОТИП/README.md` — template-readme, doc-only, вход. ссылок: 24
- `template/07_ПРОТОТИП/source/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07a_WIREFRAME/README.md` — template-readme, doc-only, вход. ссылок: 28
- `template/07b_COMPOSED/README.md` — template-readme, doc-only, вход. ссылок: 28
- `template/07c_PHOTOS/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/07c_PHOTOS/inbox/до_после/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07c_PHOTOS/inbox/документы_сертификаты/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07c_PHOTOS/inbox/интерьер_экстерьер/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07c_PHOTOS/inbox/объекты_и_продукты/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07c_PHOTOS/inbox/портреты_и_команда/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07c_PHOTOS/inbox/процесс_работы/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/07d_VISUALS/README.md` — template-readme, doc-only, вход. ссылок: 24
- `template/08_КОД/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/08_КОД/legal-pages/README.md` — template-readme, doc-only, вход. ссылок: 6
- `template/09_ДЕПЛОЙ/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/10_QA/README.md` — template-readme, doc-only, вход. ссылок: 24
- `template/11_АНАЛИТИКА/README.md` — template-readme, doc-only, вход. ссылок: 20
- `template/12_SEO/README.md` — template-readme, doc-only, вход. ссылок: 24
- `template/13_СЕГМЕНТЫ_ЦА/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/13_СЕГМЕНТЫ_ЦА/_skeleton/README.md` — template-readme, doc-only, вход. ссылок: 4
- `template/README.md` — template-readme, doc-only, вход. ссылок: 6
- `template/memory/README.md` — template-readme, doc-only, вход. ссылок: 28
- `template/wiki/README.md` — template-readme, doc-only, вход. ссылок: 28

### Кластер `SKILL-*` (27 файлов)

- `skills/block-composition/SKILL.md` — skill, active, вход. ссылок: 987
- `skills/block-library-management/SKILL.md` — skill, active, вход. ссылок: 834
- `skills/brand-kit-build/SKILL.md` — skill, active, вход. ссылок: 111
- `skills/client-assets-collection/SKILL.md` — skill, active, вход. ссылок: 59
- `skills/design-tokens-generation/SKILL.md` — skill, active, вход. ссылок: 296
- `skills/gpt5-prompting-engine/SKILL.md` — skill, active, вход. ссылок: 72
- `skills/landing-from-context/SKILL.md` — skill, active, вход. ссылок: 132
- `skills/landing-onboarding/SKILL.md` — skill, active, вход. ссылок: 317
- `skills/landing-project-init/SKILL.md` — skill, active, вход. ссылок: 164
- `skills/landing-versioning-and-cloning/SKILL.md` — skill, active, вход. ссылок: 79
- `skills/moodboard-creation/SKILL.md` — skill, active, вход. ссылок: 63
- `skills/niche-analysis/SKILL.md` — skill, active, вход. ссылок: 244
- `skills/paralaximus-codex/SKILL.md` — skill, active, вход. ссылок: 90
- `skills/photo-curation/SKILL.md` — skill, active, вход. ссылок: 189
- `skills/photo-styling/SKILL.md` — skill, active, вход. ссылок: 69
- `skills/prototype-import/SKILL.md` — skill, active, вход. ссылок: 122
- `skills/references-collection/SKILL.md` — skill, active, вход. ссылок: 58
- `skills/seo-tech-audit/SKILL.md` — skill, active, вход. ссылок: 17
- `skills/style-decomposition/SKILL.md` — skill, active, вход. ссылок: 83
- `skills/visual-generation/SKILL.md` — skill, active, вход. ссылок: 184
- `skills/visual-qa/SKILL.md` — skill, active, вход. ссылок: 121
- `skills/wireframe-rendering/SKILL.md` — skill, active, вход. ссылок: 613
- `skills/wp-cli-deployer/SKILL.md` — skill, active, вход. ссылок: 169
- `skills/wp-gutenberg-block-builder/SKILL.md` — skill, active, вход. ссылок: 256
- `skills/wp-landing-config/SKILL.md` — skill, active, вход. ссылок: 64
- `skills/wp-multisite/SKILL.md` — skill, active, вход. ссылок: 35
- `skills/wp-theme-assembler/SKILL.md` — skill, active, вход. ссылок: 124

### Кластер `__init__-*` (8 файлов)

- `scripts/wiki/__init__.py` — script, doc-only, вход. ссылок: 58
- `scripts/wiki/hooks/__init__.py` — script, doc-only, вход. ссылок: 58
- `scripts/wiki/parsers/__init__.py` — script, doc-only, вход. ссылок: 58
- `scripts/wiki/prompts/__init__.py` — script, doc-only, вход. ссылок: 58
- `skills/photo-curation/scripts/__init__.py` — skill-script, doc-only, вход. ссылок: 58
- `skills/seo-tech-audit/scripts/lib/__init__.py` — skill-script, doc-only, вход. ссылок: 58
- `skills/seo-tech-audit/scripts/runners/__init__.py` — skill-script, doc-only, вход. ссылок: 58
- `skills/visual-generation/scripts/__init__.py` — skill-script, doc-only, вход. ссылок: 58

### Кластер `admin-*` (15 файлов)

- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta-readonly.php` — mu-plugin-php, active, вход. ссылок: 20
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-cta.php` — mu-plugin-php, active, вход. ссылок: 50
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations-readonly.php` — mu-plugin-php, active, вход. ссылок: 20
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php` — mu-plugin-php, active, вход. ссылок: 72
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php` — mu-plugin-php, active, вход. ссылок: 20
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php` — mu-plugin-php, active, вход. ссылок: 20
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php` — mu-plugin-php, active, вход. ссылок: 20
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads-network.php` — mu-plugin-php, active, вход. ссылок: 16
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php` — mu-plugin-php, active, вход. ссылок: 43
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-pages.php` — mu-plugin-php, active, вход. ссылок: 32
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-readonly.php` — mu-plugin-php, active, вход. ссылок: 24
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php` — mu-plugin-php, active, вход. ссылок: 39
- `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-network.php` — mu-plugin-php, active, вход. ссылок: 7
- `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/admin-site-readonly.php` — mu-plugin-php, active, вход. ссылок: 5
- `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/admin-network.php` — mu-plugin-php, active, вход. ссылок: 7

### Кластер `ai-*` (2 файлов)

- `skills/seo-tech-audit/scripts/runners/ai_readiness.py` — skill-script, doc-only, вход. ссылок: 10
- `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/ai_readiness.php` — mu-plugin-php, doc-only, вход. ссылок: 2

### Кластер `backport-*` (2 файлов)

- `scripts/backport-acf-to-legacy.sh` — script, active, вход. ссылок: 35
- `scripts/backport-acf-to-legacy.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `block-*` (4 файлов)

- `agents/block-composer.md` — agent, active, вход. ссылок: 941
- `scripts/block-loader.py` — script, active, вход. ссылок: 24
- `scripts/block-loader.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/wp-gutenberg-block-builder/scripts/lib/block_spec.py` — skill-script, doc-only, вход. ссылок: 9

### Кластер `build-*` (6 файлов)

- `scripts/build-zip.sh` — script, active, вход. ссылок: 33
- `scripts/build-zip.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/extract-effects/build-patterns-library.py` — script, active, вход. ссылок: 27
- `scripts/extract-effects/build-patterns-library.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/brand-kit-build/scripts/build.py` — skill-script, active, вход. ссылок: 45
- `skills/design-tokens-generation/scripts/build-tokens.py` — skill-script, active, вход. ссылок: 67

### Кластер `check-*` (9 файлов)

- `scripts/check-deps.sh` — script, active, вход. ссылок: 70
- `scripts/check-deps.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/check-wiki-sync.sh` — script, active, вход. ссылок: 64
- `scripts/check-wiki-sync.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/checks/check_legal_blocks.sh` — script, active, вход. ссылок: 8
- `scripts/lib/check-block-registration.sh` — script, doc-only, вход. ссылок: 26
- `scripts/lib/check-block-registration.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/wp-gutenberg-block-builder/scripts/check-block-php-markers.py` — skill-script, active, вход. ссылок: 35
- `skills/wp-gutenberg-block-builder/scripts/check-section5-css.py` — skill-script, active, вход. ссылок: 19

### Кластер `cleanup-*` (2 файлов)

- `scripts/wiki/cleanup_broken_links.py` — script, doc-only, вход. ссылок: 20
- `scripts/wiki/cleanup_broken_links.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `clone-*` (2 файлов)

- `skills/landing-versioning-and-cloning/scripts/clone-landing.sh` — skill-script, active, вход. ссылок: 56
- `skills/wp-multisite/scripts/clone-subsite.sh` — skill-script, active, вход. ссылок: 31

### Кластер `codex-*` (9 файлов)

- `scripts/import-blocks/codex-analyze-structure.sh` — script, active, вход. ссылок: 20
- `scripts/import-blocks/codex-analyze-structure.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/photo-curation/scripts/codex-classify.sh` — skill-script, active, вход. ссылок: 43
- `skills/photo-curation/scripts/codex-generate-fallback.sh` — skill-script, active, вход. ссылок: 43
- `skills/photo-curation/scripts/codex-match.sh` — skill-script, active, вход. ссылок: 35
- `skills/photo-curation/scripts/codex-process-photo.sh` — skill-script, active, вход. ссылок: 52
- `skills/visual-generation/scripts/codex-generate-icon.sh` — skill-script, active, вход. ссылок: 56
- `skills/visual-generation/scripts/codex-generate-infographic.sh` — skill-script, active, вход. ссылок: 31
- `skills/visual-qa/scripts/codex-review-screenshot.sh` — skill-script, active, вход. ссылок: 31

### Кластер `composed-*` (3 файлов)

- `scripts/wiki/parsers/composed_html.py` — script, doc-only, вход. ссылок: 24
- `scripts/wiki/parsers/composed_html.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/wp-gutenberg-block-builder/scripts/lib/composed_inspector.py` — skill-script, doc-only, вход. ссылок: 3

### Кластер `content-*` (3 файлов)

- `agents/content-writer.md` — agent, active, вход. ссылок: 266
- `scripts/lib/content_parser.py` — script, active, вход. ссылок: 53
- `scripts/lib/content_parser.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `conversations-*` (2 файлов)

- `scripts/wiki/conversations_compiler.py` — script, active, вход. ссылок: 27
- `scripts/wiki/conversations_compiler.py.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `deploy-*` (2 файлов)

- `scripts/deploy.sh` — script, active, вход. ссылок: 156
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — skill-script, active, вход. ссылок: 94

### Кластер `derive-*` (2 файлов)

- `scripts/derive-landing-structure.py` — script, active, вход. ссылок: 47
- `scripts/derive-landing-structure.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `design-*` (2 файлов)

- `agents/design-system-generator.md` — agent, active, вход. ссылок: 278
- `skills/wp-gutenberg-block-builder/scripts/lib/design_extractor.py` — skill-script, active, вход. ссылок: 8

### Кластер `export-*` (2 файлов)

- `scripts/export-palettes-to-library.py` — script, active, вход. ссылок: 52
- `scripts/export-palettes-to-library.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `extract-*` (5 файлов)

- `scripts/extract-effects/extract-patterns.py` — script, active, вход. ссылок: 27
- `scripts/extract-effects/extract-patterns.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/prototype-import/scripts/extract-pdf-text.py` — skill-script, active, вход. ссылок: 35
- `skills/style-decomposition/scripts/extract-palette.py` — skill-script, active, вход. ссылок: 57
- `skills/wp-gutenberg-block-builder/scripts/extract-main-css.py` — skill-script, active, вход. ссылок: 37

### Кластер `fix-*` (2 файлов)

- `skills/seo-tech-audit/scripts/lib/fix_actions.py` — skill-script, doc-only, вход. ссылок: 2
- `skills/wp-cli-deployer/scripts/fix-page-content-images.py` — skill-script, active, вход. ссылок: 8

### Кластер `floating-*` (2 файлов)

- `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/floating-card-left.php` — mu-plugin-php, doc-only, вход. ссылок: 2
- `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/layouts/floating-card-right.php` — mu-plugin-php, doc-only, вход. ссылок: 2

### Кластер `gate-*` (4 файлов)

- `scripts/gate-check.sh` — script, active, вход. ссылок: 649
- `scripts/gate-check.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/gate-state.sh` — script, active, вход. ссылок: 193
- `scripts/gate-state.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `generate-*` (21 файлов)

- `scripts/generate-axes-filter.py` — script, active, вход. ссылок: 49
- `scripts/generate-axes-filter.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/generate-palette-css.py` — script, active, вход. ссылок: 49
- `scripts/generate-palette-css.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/generate-previews.sh` — script, active, вход. ссылок: 27
- `scripts/generate-previews.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/generate-script-docs.py` — script, active, вход. ссылок: 11
- `scripts/generate-wp-blocks.py` — script, active, вход. ссылок: 92
- `scripts/generate-wp-blocks.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/import-blocks/generate-blocks.py` — script, active, вход. ссылок: 20
- `scripts/import-blocks/generate-blocks.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/paralaximus-codex/scripts/generate-atlas.sh` — skill-script, active, вход. ссылок: 70
- `skills/wp-gutenberg-block-builder/scripts/generate-analytics.py` — skill-script, active, вход. ссылок: 49
- `skills/wp-gutenberg-block-builder/scripts/generate-css-patches.py` — skill-script, active, вход. ссылок: 65
- `skills/wp-gutenberg-block-builder/scripts/generate-integrations.py` — skill-script, active, вход. ссылок: 49
- `skills/wp-gutenberg-block-builder/scripts/generate-js-init.py` — skill-script, active, вход. ссылок: 43
- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py` — skill-script, active, вход. ссылок: 64
- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py` — skill-script, active, вход. ссылок: 73
- `skills/wp-gutenberg-block-builder/scripts/generate-page-content.py` — skill-script, active, вход. ссылок: 71
- `skills/wp-gutenberg-block-builder/scripts/generate-popup.py` — skill-script, active, вход. ссылок: 43
- `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` — skill-script, active, вход. ссылок: 135

### Кластер `hash-*` (2 файлов)

- `scripts/wiki/hash_cache.py` — script, doc-only, вход. ссылок: 24
- `scripts/wiki/hash_cache.py.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `head-*` (2 файлов)

- `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo-admin.php` — mu-plugin-php, active, вход. ссылок: 6
- `skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php` — mu-plugin-php, active, вход. ссылок: 27

### Кластер `html-*` (2 файлов)

- `skills/seo-tech-audit/scripts/runners/html_checks.py` — skill-script, doc-only, вход. ссылок: 9
- `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/html.php` — mu-plugin-php, doc-only, вход. ссылок: 3

### Кластер `import-*` (2 файлов)

- `scripts/import-blocks/import-from-url.sh` — script, active, вход. ссылок: 34
- `scripts/import-blocks/import-from-url.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `inject-*` (2 файлов)

- `skills/block-composition/scripts/inject-content.py` — skill-script, active, вход. ссылок: 88
- `skills/block-composition/scripts/inject-tokens.py` — skill-script, active, вход. ссылок: 75

### Кластер `install-*` (6 файлов)

- `scripts/install-codex.sh` — script, active, вход. ссылок: 72
- `scripts/install-codex.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/install-git-hooks.sh` — script, doc-only, вход. ссылок: 43
- `scripts/install-git-hooks.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/wp-builder/scripts/install_legal_pages.sh` — skill-script, active, вход. ссылок: 8
- `skills/wp-landing-config/scripts/install-mu-plugin.sh` — skill-script, active, вход. ссылок: 46

### Кластер `integrations-*` (2 файлов)

- `agents/integrations-engineer.md` — agent, active, вход. ссылок: 178
- `skills/wp-landing-config/mu-plugin/landing-config/includes/integrations.php` — mu-plugin-php, active, вход. ссылок: 84

### Кластер `landing-*` (70 файлов)

- `.claude/commands/landing-admin-install.md` — command-dot-claude, active, вход. ссылок: 23
- `.claude/commands/landing-audit.md` — command-dot-claude, active, вход. ссылок: 12
- `.claude/commands/landing-brand.md` — command-dot-claude, active, вход. ссылок: 162
- `.claude/commands/landing-build.md` — command-dot-claude, active, вход. ссылок: 397
- `.claude/commands/landing-clone.md` — command-dot-claude, active, вход. ссылок: 132
- `.claude/commands/landing-compose.md` — command-dot-claude, active, вход. ссылок: 196
- `.claude/commands/landing-content.md` — command-dot-claude, active, вход. ссылок: 161
- `.claude/commands/landing-deploy.md` — command-dot-claude, active, вход. ссылок: 290
- `.claude/commands/landing-design.md` — command-dot-claude, active, вход. ссылок: 220
- `.claude/commands/landing-final-check.md` — command-dot-claude, active, вход. ссылок: 55
- `.claude/commands/landing-from-context.md` — command-dot-claude, active, вход. ссылок: 132
- `.claude/commands/landing-go.md` — command-dot-claude, active, вход. ссылок: 268
- `.claude/commands/landing-help.md` — command-dot-claude, active, вход. ссылок: 72
- `.claude/commands/landing-import-blocks.md` — command-dot-claude, active, вход. ссылок: 48
- `.claude/commands/landing-moodboard.md` — command-dot-claude, active, вход. ссылок: 102
- `.claude/commands/landing-new.md` — command-dot-claude, active, вход. ссылок: 266
- `.claude/commands/landing-niche.md` — command-dot-claude, active, вход. ссылок: 103
- `.claude/commands/landing-onboarding.md` — command-dot-claude, active, вход. ссылок: 318
- `.claude/commands/landing-photos.md` — command-dot-claude, active, вход. ссылок: 203
- `.claude/commands/landing-previews.md` — command-dot-claude, active, вход. ссылок: 31
- `.claude/commands/landing-prototype.md` — command-dot-claude, active, вход. ссылок: 142
- `.claude/commands/landing-qa.md` — command-dot-claude, active, вход. ссылок: 190
- `.claude/commands/landing-references.md` — command-dot-claude, active, вход. ссылок: 153
- `.claude/commands/landing-rollback.md` — command-dot-claude, active, вход. ссылок: 118
- `.claude/commands/landing-segment.md` — command-dot-claude, active, вход. ссылок: 63
- `.claude/commands/landing-setup.md` — command-dot-claude, active, вход. ссылок: 94
- `.claude/commands/landing-stack.md` — command-dot-claude, active, вход. ссылок: 168
- `.claude/commands/landing-start.md` — command-dot-claude, active, вход. ссылок: 153
- `.claude/commands/landing-status.md` — command-dot-claude, active, вход. ссылок: 135
- `.claude/commands/landing-style.md` — command-dot-claude, active, вход. ссылок: 70
- `.claude/commands/landing-visuals.md` — command-dot-claude, active, вход. ссылок: 158
- `.claude/commands/landing-wireframe.md` — command-dot-claude, active, вход. ссылок: 172
- `agents/landing-onboarding-wizard.md` — agent, active, вход. ссылок: 71
- `agents/landing-orchestrator.md` — agent, active, вход. ссылок: 707
- `commands/landing-brand.md` — command-root, active, вход. ссылок: 162
- `commands/landing-build.md` — command-root, active, вход. ссылок: 397
- `commands/landing-clone.md` — command-root, active, вход. ссылок: 132
- `commands/landing-compose.md` — command-root, active, вход. ссылок: 196
- `commands/landing-content.md` — command-root, active, вход. ссылок: 161
- `commands/landing-deploy.md` — command-root, active, вход. ссылок: 290
- `commands/landing-design.md` — command-root, active, вход. ссылок: 220
- `commands/landing-final-check.md` — command-root, active, вход. ссылок: 55
- `commands/landing-from-context.md` — command-root, active, вход. ссылок: 132
- `commands/landing-go.md` — command-root, active, вход. ссылок: 268
- `commands/landing-help.md` — command-root, active, вход. ссылок: 72
- `commands/landing-import-blocks.md` — command-root, active, вход. ссылок: 48
- `commands/landing-moodboard.md` — command-root, active, вход. ссылок: 102
- `commands/landing-new.md` — command-root, active, вход. ссылок: 266
- `commands/landing-niche.md` — command-root, active, вход. ссылок: 103
- `commands/landing-onboarding.md` — command-root, active, вход. ссылок: 318
- `commands/landing-photos.md` — command-root, active, вход. ссылок: 203
- `commands/landing-previews.md` — command-root, active, вход. ссылок: 31
- `commands/landing-prototype.md` — command-root, active, вход. ссылок: 142
- `commands/landing-qa.md` — command-root, active, вход. ссылок: 190
- `commands/landing-references.md` — command-root, active, вход. ссылок: 153
- `commands/landing-rollback.md` — command-root, active, вход. ссылок: 118
- `commands/landing-setup.md` — command-root, active, вход. ссылок: 94
- `commands/landing-stack.md` — command-root, active, вход. ссылок: 168
- `commands/landing-start.md` — command-root, active, вход. ссылок: 153
- `commands/landing-status.md` — command-root, active, вход. ссылок: 135
- `commands/landing-style.md` — command-root, active, вход. ссылок: 70
- `commands/landing-visuals.md` — command-root, active, вход. ссылок: 158
- `commands/landing-wireframe.md` — command-root, active, вход. ссылок: 172
- `scripts/landing-final-check.sh` — script, active, вход. ссылок: 35
- `scripts/landing-final-check.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/landing-go-next-stage.py` — script, active, вход. ссылок: 39
- `scripts/landing-go-next-stage.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/wp-landing-config/mu-plugin/landing-config-loader.php` — mu-plugin-php, active, вход. ссылок: 11
- `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — mu-plugin-php, active, вход. ссылок: 92
- `skills/wp-multisite/scripts/landing-segment.sh` — skill-script, active, вход. ссылок: 31

### Кластер `lead-*` (2 файлов)

- `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-status-log.php` — mu-plugin-php, active, вход. ссылок: 36
- `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-statuses.php` — mu-plugin-php, active, вход. ссылок: 52

### Кластер `lint-*` (3 файлов)

- `scripts/wiki/lint.py` — script, doc-only, вход. ссылок: 55
- `skills/wp-gutenberg-block-builder/scripts/lib/lint_heuristics.py` — skill-script, active, вход. ссылок: 4
- `skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py` — skill-script, doc-only, вход. ссылок: 6

### Кластер `mark-*` (2 файлов)

- `scripts/mark-legacy-projects.sh` — script, active, вход. ссылок: 35
- `scripts/mark-legacy-projects.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `match-*` (3 файлов)

- `skills/photo-curation/scripts/match-photos-to-slots.py` — skill-script, active, вход. ссылок: 7
- `skills/style-decomposition/scripts/match-icons.py` — skill-script, active, вход. ссылок: 57
- `skills/wireframe-rendering/scripts/match-candidates.py` — skill-script, active, вход. ссылок: 28

### Кластер `migrate-*` (17 файлов)

- `scripts/migrate-add-wiki.sh` — script, active, вход. ссылок: 43
- `scripts/migrate-add-wiki.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/migrate-blocks-to-wireframe-format.py` — script, doc-only, вход. ссылок: 16
- `scripts/migrate-blocks-to-wireframe-format.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-niche-to-v2.sh` — script, active, вход. ссылок: 43
- `scripts/migrate-niche-to-v2.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-state-add-01a.sh` — script, active, вход. ссылок: 35
- `scripts/migrate-state-add-01a.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-state-for-prd.sh` — script, active, вход. ссылок: 39
- `scripts/migrate-state-for-prd.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-template-readmes.sh` — script, active, вход. ссылок: 39
- `scripts/migrate-template-readmes.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/migrate-to-preview-panel.sh` — script, active, вход. ссылок: 37
- `scripts/migrate-to-preview-panel.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/migrate.php` — mu-plugin-php, active, вход. ссылок: 7
- `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php` — mu-plugin-php, active, вход. ссылок: 40
- `skills/wp-multisite/scripts/migrate-to-multisite.sh` — skill-script, active, вход. ссылок: 31

### Кластер `network-*` (2 файлов)

- `skills/seo-tech-audit/scripts/runners/network_checks.py` — skill-script, doc-only, вход. ссылок: 9
- `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/network.php` — mu-plugin-php, active, вход. ссылок: 40

### Кластер `niche-*` (2 файлов)

- `agents/niche-analyst.md` — agent, active, вход. ссылок: 222
- `config/niche-visual-rules.yaml` — config, active, вход. ссылок: 67

### Кластер `parse-*` (2 файлов)

- `skills/brand-kit-build/scripts/parse_legal.py` — skill-script, active, вход. ссылок: 9
- `skills/client-assets-collection/scripts/parse-reviews.py` — skill-script, active, вход. ссылок: 44

### Кластер `photo-*` (6 файлов)

- `agents/photo-classifier.md` — agent, active, вход. ссылок: 103
- `agents/photo-curator.md` — agent, active, вход. ссылок: 403
- `agents/photo-matcher.md` — agent, active, вход. ссылок: 107
- `agents/photo-preview-board.md` — agent, active, вход. ссылок: 112
- `agents/photo-stylist.md` — agent, active, вход. ссылок: 124
- `skills/photo-curation/scripts/photo-pipeline.py` — skill-script, active, вход. ссылок: 55

### Кластер `pre-*` (2 файлов)

- `scripts/wiki/hooks/pre_compact.py` — script, doc-only, вход. ссылок: 36
- `scripts/wiki/hooks/pre_compact.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `preview-*` (4 файлов)

- `scripts/preview-blocks-library.py` — script, active, вход. ссылок: 19
- `scripts/preview-blocks-library.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/wiki/preview.py` — script, active, вход. ссылок: 153
- `skills/photo-curation/scripts/preview-render.py` — skill-script, active, вход. ссылок: 24

### Кластер `project-*` (2 файлов)

- `scripts/wiki/project_graph_compiler.py` — script, active, вход. ссылок: 31
- `scripts/wiki/project_graph_compiler.py.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `refresh-*` (2 файлов)

- `scripts/refresh-catalog.py` — script, doc-only, вход. ссылок: 16
- `scripts/refresh-catalog.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `render-*` (11 файлов)

- `scripts/render-pipeline-map.sh` — script, active, вход. ссылок: 131
- `scripts/render-pipeline-map.sh.doc.md` — script-doc, doc-only, вход. ссылок: 9
- `skills/block-library-management/scripts/render-gallery.py` — skill-script, active, вход. ссылок: 7
- `skills/brand-kit-build/scripts/render-html.py` — skill-script, active, вход. ссылок: 40
- `skills/design-tokens-generation/scripts/render-preview.py` — skill-script, active, вход. ссылок: 61
- `skills/legal-pages-render/scripts/render.py` — skill-script, active, вход. ссылок: 85
- `skills/moodboard-creation/scripts/render.py` — skill-script, active, вход. ссылок: 84
- `skills/photo-curation/scripts/render-prompt.py` — skill-script, active, вход. ссылок: 52
- `skills/wireframe-rendering/scripts/render-wireframe.py` — skill-script, active, вход. ссылок: 37
- `skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/render.php` — mu-plugin-php, active, вход. ссылок: 15
- `skills/wp-theme-assembler/scripts/render-build-preview.py` — skill-script, active, вход. ссылок: 66

### Кластер `scaffold-*` (2 файлов)

- `skills/block-library-management/scripts/scaffold-block.py` — skill-script, active, вход. ссылок: 43
- `skills/moodboard-creation/scripts/scaffold.py` — skill-script, active, вход. ссылок: 21

### Кластер `schema-*` (2 файлов)

- `skills/seo-tech-audit/scripts/runners/schema_checks.py` — skill-script, doc-only, вход. ссылок: 9
- `skills/wp-landing-config/mu-plugin/landing-config/includes/seo-audit/tabs/schema.php` — mu-plugin-php, active, вход. ссылок: 25

### Кластер `scrape-*` (2 файлов)

- `scripts/extract-effects/scrape-css.sh` — script, active, вход. ссылок: 23
- `scripts/extract-effects/scrape-css.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `sdk-*` (2 файлов)

- `scripts/wiki/sdk_client.py` — script, doc-only, вход. ссылок: 27
- `scripts/wiki/sdk_client.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `selections-*` (3 файлов)

- `scripts/wiki/parsers/selections_yaml.py` — script, doc-only, вход. ссылок: 20
- `scripts/wiki/parsers/selections_yaml.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/photo-curation/scripts/selections-validator.py` — skill-script, active, вход. ссылок: 47

### Кластер `session-*` (4 файлов)

- `scripts/wiki/hooks/session_end.py` — script, doc-only, вход. ссылок: 36
- `scripts/wiki/hooks/session_end.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/wiki/hooks/session_start.py` — script, doc-only, вход. ссылок: 36
- `scripts/wiki/hooks/session_start.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `setup-*` (2 файлов)

- `scripts/setup-flag.sh` — script, active, вход. ссылок: 220
- `scripts/setup-flag.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `snapshot-*` (2 файлов)

- `scripts/snapshot-palettes-to-project.py` — script, active, вход. ссылок: 40
- `scripts/snapshot-palettes-to-project.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `stage-*` (6 файлов)

- `config/stage-gates.yaml` — config, active, вход. ссылок: 319
- `docs/standards/stage-08-spec-lint.md` — standard, doc-only, вход. ссылок: 3
- `docs/standards/stage-agent-preamble.md` — standard, doc-only, вход. ссылок: 15
- `docs/standards/stage-execution-protocol.md` — standard, active, вход. ссылок: 94
- `scripts/lib/stage_08_helper.py` — script, active, вход. ссылок: 43
- `scripts/lib/stage_08_helper.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `state-*` (3 файлов)

- `scripts/wiki/parsers/state_yaml.py` — script, doc-only, вход. ссылок: 20
- `scripts/wiki/parsers/state_yaml.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/wp-multisite/scripts/lib/state.sh` — skill-script, active, вход. ссылок: 214

### Кластер `style-*` (8 файлов)

- `agents/style-extractor.md` — agent, active, вход. ссылок: 153
- `block-library/_styles/brutalist/style-guide.md` — style-guide, active, вход. ссылок: 214
- `block-library/_styles/coral-soft/style-guide.md` — style-guide, active, вход. ссылок: 17
- `block-library/_styles/editorial-warm/style-guide.md` — style-guide, active, вход. ссылок: 37
- `block-library/_styles/monochrome-precision/style-guide.md` — style-guide, active, вход. ссылок: 17
- `block-library/_styles/retro-windows/style-guide.md` — style-guide, active, вход. ссылок: 24
- `block-library/_styles/swiss-modernist/style-guide.md` — style-guide, active, вход. ссылок: 17
- `skills/photo-styling/scripts/style.py` — skill-script, active, вход. ссылок: 66

### Кластер `system-*` (3 файлов)

- `agents/system-setup.md` — agent, active, вход. ссылок: 82
- `scripts/wiki/system_compiler.py` — script, doc-only, вход. ссылок: 33
- `scripts/wiki/system_compiler.py.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `take-*` (3 файлов)

- `scripts/import-blocks/take-page-screenshot.py` — script, active, вход. ссылок: 20
- `scripts/import-blocks/take-page-screenshot.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/visual-qa/scripts/take-screenshots.py` — skill-script, active, вход. ссылок: 35

### Кластер `test-*` (3 файлов)

- `scripts/test-pipeline.sh` — script, active, вход. ссылок: 60
- `scripts/test-pipeline.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/wp-landing-config/scripts/test-smoke-rest.sh` — skill-script, active, вход. ссылок: 15

### Кластер `tokens-*` (2 файлов)

- `scripts/wiki/parsers/tokens_json.py` — script, doc-only, вход. ссылок: 20
- `scripts/wiki/parsers/tokens_json.py.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `update-*` (2 файлов)

- `scripts/import-blocks/update-catalog.py` — script, active, вход. ссылок: 20
- `scripts/import-blocks/update-catalog.py.doc.md` — script-doc, doc-only, вход. ссылок: 12

### Кластер `validate-*` (13 файлов)

- `scripts/validate-all.sh` — script, active, вход. ссылок: 106
- `scripts/validate-all.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/validate-palettes.py` — script, active, вход. ссылок: 51
- `scripts/validate-palettes.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `skills/block-composition/scripts/validate-selections.py` — skill-script, active, вход. ссылок: 39
- `skills/block-library-management/scripts/validate-catalog.py` — skill-script, active, вход. ссылок: 31
- `skills/block-library-management/scripts/validate-meta.py` — skill-script, active, вход. ссылок: 31
- `skills/niche-analysis/scripts/validate-competitors.py` — skill-script, active, вход. ссылок: 79
- `skills/niche-analysis/scripts/validate-landing-structure.py` — skill-script, active, вход. ссылок: 53
- `skills/niche-analysis/scripts/validate-market-profile.py` — skill-script, active, вход. ссылок: 53
- `skills/niche-analysis/scripts/validate-positioning.py` — skill-script, active, вход. ссылок: 53
- `skills/niche-analysis/scripts/validate-visual-requirements.py` — skill-script, active, вход. ссылок: 55
- `skills/prototype-import/scripts/validate-prototype.py` — skill-script, active, вход. ссылок: 52

### Кластер `verify-*` (24 файлов)

- `scripts/verify-composed-has-visuals.sh` — script, active, вход. ссылок: 39
- `scripts/verify-composed-has-visuals.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/verify-composed-premium.sh` — script, active, вход. ссылок: 102
- `scripts/verify-composed-premium.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/verify-content-preserved.sh` — script, active, вход. ссылок: 66
- `scripts/verify-content-preserved.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/verify-gutenberg-json.sh` — script, active, вход. ссылок: 39
- `scripts/verify-gutenberg-json.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/verify-identity-preserved.sh` — script, active, вход. ссылок: 59
- `scripts/verify-identity-preserved.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/verify-photo-pipeline.sh` — script, active, вход. ссылок: 58
- `scripts/verify-photo-pipeline.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/verify-php-syntax.sh` — script, active, вход. ссылок: 39
- `scripts/verify-php-syntax.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/verify-site-url.sh` — script, active, вход. ссылок: 39
- `scripts/verify-site-url.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/verify-visual-qa.sh` — script, active, вход. ссылок: 49
- `scripts/verify-visual-qa.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/verify_content_preserved.py` — script, active, вход. ссылок: 47
- `scripts/verify_content_preserved.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/verify_photo_pipeline.py` — script, active, вход. ссылок: 39
- `scripts/verify_photo_pipeline.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/verify_visual_qa.py` — script, active, вход. ссылок: 38
- `scripts/verify_visual_qa.py.doc.md` — script-doc, doc-only, вход. ссылок: 8

### Кластер `visual-*` (3 файлов)

- `agents/visual-curator.md` — agent, active, вход. ссылок: 193
- `skills/visual-generation/scripts/visual-cache.py` — skill-script, active, вход. ссылок: 36
- `skills/visual-qa/scripts/visual-qa-loop.py` — skill-script, active, вход. ссылок: 35

### Кластер `wizard-*` (3 файлов)

- `scripts/wizard-check-materials.py` — script, active, вход. ссылок: 60
- `scripts/wizard-check-materials.py.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/wizard.sh` — script, active, вход. ссылок: 104

### Кластер `wp-*` (2 файлов)

- `agents/wp-builder.md` — agent, active, вход. ссылок: 450
- `agents/wp-deployer.md` — agent, active, вход. ссылок: 201

## Файлы с префиксом `_`

Список (соглашение `_` часто означает «приватный» или «одноразовый»):

- `scripts/_migrate-extract-palettes.py` — script, active, вход. ссылок: 12
- `scripts/_migrate-strip-header.py` — script, active, вход. ссылок: 12
- `scripts/_migrate-strip-js.py` — script, active, вход. ссылок: 12
- `scripts/wiki/__init__.py` — script, doc-only, вход. ссылок: 58
- `scripts/wiki/hooks/__init__.py` — script, doc-only, вход. ссылок: 58
- `scripts/wiki/parsers/__init__.py` — script, doc-only, вход. ссылок: 58
- `scripts/wiki/prompts/__init__.py` — script, doc-only, вход. ссылок: 58
- `skills/photo-curation/scripts/__init__.py` — skill-script, doc-only, вход. ссылок: 58
- `skills/seo-tech-audit/scripts/lib/__init__.py` — skill-script, doc-only, вход. ссылок: 58
- `skills/seo-tech-audit/scripts/runners/__init__.py` — skill-script, doc-only, вход. ссылок: 58
- `skills/visual-generation/scripts/__init__.py` — skill-script, doc-only, вход. ссылок: 58

## Migration-скрипты

Файлы с именем, попадающим под паттерны `^migrate-`, `-migrate.`, `^backport-`, `^_migrate-`.

- `scripts/_migrate-extract-palettes.py` — script, active, вход. ссылок: 12
- `scripts/_migrate-strip-header.py` — script, active, вход. ссылок: 12
- `scripts/_migrate-strip-js.py` — script, active, вход. ссылок: 12
- `scripts/backport-acf-to-legacy.sh` — script, active, вход. ссылок: 35
- `scripts/backport-acf-to-legacy.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-add-wiki.sh` — script, active, вход. ссылок: 43
- `scripts/migrate-add-wiki.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/migrate-blocks-to-wireframe-format.py` — script, doc-only, вход. ссылок: 16
- `scripts/migrate-blocks-to-wireframe-format.py.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-niche-to-v2.sh` — script, active, вход. ссылок: 43
- `scripts/migrate-niche-to-v2.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-state-add-01a.sh` — script, active, вход. ссылок: 35
- `scripts/migrate-state-add-01a.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-state-for-prd.sh` — script, active, вход. ссылок: 39
- `scripts/migrate-state-for-prd.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `scripts/migrate-template-readmes.sh` — script, active, вход. ссылок: 39
- `scripts/migrate-template-readmes.sh.doc.md` — script-doc, doc-only, вход. ссылок: 12
- `scripts/migrate-to-preview-panel.sh` — script, active, вход. ссылок: 37
- `scripts/migrate-to-preview-panel.sh.doc.md` — script-doc, doc-only, вход. ссылок: 8
- `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php` — mu-plugin-php, active, вход. ссылок: 40
- `skills/wp-multisite/scripts/migrate-to-multisite.sh` — skill-script, active, вход. ссылок: 31

## `.doc.md` пары (auto-doc для скриптов)

Для каждой пары: путь к `.doc.md`, ожидаемый исполняемый файл, существует ли он.

| `.doc.md` | Исполняемый файл | Существует |
|---|---|:---:|
| `scripts/backport-acf-to-legacy.sh.doc.md` | `scripts/backport-acf-to-legacy.sh` | да |
| `scripts/block-loader.py.doc.md` | `scripts/block-loader.py` | да |
| `scripts/build-zip.sh.doc.md` | `scripts/build-zip.sh` | да |
| `scripts/check-deps.sh.doc.md` | `scripts/check-deps.sh` | да |
| `scripts/check-wiki-sync.sh.doc.md` | `scripts/check-wiki-sync.sh` | да |
| `scripts/deploy.sh.doc.md` | `scripts/deploy.sh` | да |
| `scripts/derive-landing-structure.py.doc.md` | `scripts/derive-landing-structure.py` | да |
| `scripts/export-palettes-to-library.py.doc.md` | `scripts/export-palettes-to-library.py` | да |
| `scripts/extract-effects/build-patterns-library.py.doc.md` | `scripts/extract-effects/build-patterns-library.py` | да |
| `scripts/extract-effects/extract-patterns.py.doc.md` | `scripts/extract-effects/extract-patterns.py` | да |
| `scripts/extract-effects/scrape-css.sh.doc.md` | `scripts/extract-effects/scrape-css.sh` | да |
| `scripts/gate-check.sh.doc.md` | `scripts/gate-check.sh` | да |
| `scripts/gate-state.sh.doc.md` | `scripts/gate-state.sh` | да |
| `scripts/generate-axes-filter.py.doc.md` | `scripts/generate-axes-filter.py` | да |
| `scripts/generate-palette-css.py.doc.md` | `scripts/generate-palette-css.py` | да |
| `scripts/generate-previews.sh.doc.md` | `scripts/generate-previews.sh` | да |
| `scripts/generate-wp-blocks.py.doc.md` | `scripts/generate-wp-blocks.py` | да |
| `scripts/import-blocks/codex-analyze-structure.sh.doc.md` | `scripts/import-blocks/codex-analyze-structure.sh` | да |
| `scripts/import-blocks/generate-blocks.py.doc.md` | `scripts/import-blocks/generate-blocks.py` | да |
| `scripts/import-blocks/import-from-url.sh.doc.md` | `scripts/import-blocks/import-from-url.sh` | да |
| `scripts/import-blocks/take-page-screenshot.py.doc.md` | `scripts/import-blocks/take-page-screenshot.py` | да |
| `scripts/import-blocks/update-catalog.py.doc.md` | `scripts/import-blocks/update-catalog.py` | да |
| `scripts/install-codex.sh.doc.md` | `scripts/install-codex.sh` | да |
| `scripts/install-git-hooks.sh.doc.md` | `scripts/install-git-hooks.sh` | да |
| `scripts/landing-final-check.sh.doc.md` | `scripts/landing-final-check.sh` | да |
| `scripts/landing-go-next-stage.py.doc.md` | `scripts/landing-go-next-stage.py` | да |
| `scripts/lib/check-block-registration.sh.doc.md` | `scripts/lib/check-block-registration.sh` | да |
| `scripts/lib/content_parser.py.doc.md` | `scripts/lib/content_parser.py` | да |
| `scripts/lib/stage_08_helper.py.doc.md` | `scripts/lib/stage_08_helper.py` | да |
| `scripts/mark-legacy-projects.sh.doc.md` | `scripts/mark-legacy-projects.sh` | да |
| `scripts/migrate-add-wiki.sh.doc.md` | `scripts/migrate-add-wiki.sh` | да |
| `scripts/migrate-blocks-to-wireframe-format.py.doc.md` | `scripts/migrate-blocks-to-wireframe-format.py` | да |
| `scripts/migrate-niche-to-v2.sh.doc.md` | `scripts/migrate-niche-to-v2.sh` | да |
| `scripts/migrate-state-add-01a.sh.doc.md` | `scripts/migrate-state-add-01a.sh` | да |
| `scripts/migrate-state-for-prd.sh.doc.md` | `scripts/migrate-state-for-prd.sh` | да |
| `scripts/migrate-template-readmes.sh.doc.md` | `scripts/migrate-template-readmes.sh` | да |
| `scripts/migrate-to-preview-panel.sh.doc.md` | `scripts/migrate-to-preview-panel.sh` | да |
| `scripts/preflight.sh.doc.md` | `scripts/preflight.sh` | да |
| `scripts/preview-blocks-library.py.doc.md` | `scripts/preview-blocks-library.py` | да |
| `scripts/refresh-catalog.py.doc.md` | `scripts/refresh-catalog.py` | да |
| `scripts/render-pipeline-map.sh.doc.md` | `scripts/render-pipeline-map.sh` | да |
| `scripts/setup-flag.sh.doc.md` | `scripts/setup-flag.sh` | да |
| `scripts/snapshot-palettes-to-project.py.doc.md` | `scripts/snapshot-palettes-to-project.py` | да |
| `scripts/test-pipeline.sh.doc.md` | `scripts/test-pipeline.sh` | да |
| `scripts/validate-all.sh.doc.md` | `scripts/validate-all.sh` | да |
| `scripts/validate-palettes.py.doc.md` | `scripts/validate-palettes.py` | да |
| `scripts/verify-composed-has-visuals.sh.doc.md` | `scripts/verify-composed-has-visuals.sh` | да |
| `scripts/verify-composed-premium.sh.doc.md` | `scripts/verify-composed-premium.sh` | да |
| `scripts/verify-content-preserved.sh.doc.md` | `scripts/verify-content-preserved.sh` | да |
| `scripts/verify-gutenberg-json.sh.doc.md` | `scripts/verify-gutenberg-json.sh` | да |
| `scripts/verify-identity-preserved.sh.doc.md` | `scripts/verify-identity-preserved.sh` | да |
| `scripts/verify-photo-pipeline.sh.doc.md` | `scripts/verify-photo-pipeline.sh` | да |
| `scripts/verify-php-syntax.sh.doc.md` | `scripts/verify-php-syntax.sh` | да |
| `scripts/verify-site-url.sh.doc.md` | `scripts/verify-site-url.sh` | да |
| `scripts/verify-visual-qa.sh.doc.md` | `scripts/verify-visual-qa.sh` | да |
| `scripts/verify_content_preserved.py.doc.md` | `scripts/verify_content_preserved.py` | да |
| `scripts/verify_photo_pipeline.py.doc.md` | `scripts/verify_photo_pipeline.py` | да |
| `scripts/verify_visual_qa.py.doc.md` | `scripts/verify_visual_qa.py` | да |
| `scripts/wiki/cleanup_broken_links.py.doc.md` | `scripts/wiki/cleanup_broken_links.py` | да |
| `scripts/wiki/compile.py.doc.md` | `scripts/wiki/compile.py` | да |
| `scripts/wiki/config.py.doc.md` | `scripts/wiki/config.py` | да |
| `scripts/wiki/conversations_compiler.py.doc.md` | `scripts/wiki/conversations_compiler.py` | да |
| `scripts/wiki/flush.py.doc.md` | `scripts/wiki/flush.py` | да |
| `scripts/wiki/hash_cache.py.doc.md` | `scripts/wiki/hash_cache.py` | да |
| `scripts/wiki/hooks/pre_compact.py.doc.md` | `scripts/wiki/hooks/pre_compact.py` | да |
| `scripts/wiki/hooks/session_end.py.doc.md` | `scripts/wiki/hooks/session_end.py` | да |
| `scripts/wiki/hooks/session_start.py.doc.md` | `scripts/wiki/hooks/session_start.py` | да |
| `scripts/wiki/lint.py.doc.md` | `scripts/wiki/lint.py` | да |
| `scripts/wiki/parsers/composed_html.py.doc.md` | `scripts/wiki/parsers/composed_html.py` | да |
| `scripts/wiki/parsers/selections_yaml.py.doc.md` | `scripts/wiki/parsers/selections_yaml.py` | да |
| `scripts/wiki/parsers/state_yaml.py.doc.md` | `scripts/wiki/parsers/state_yaml.py` | да |
| `scripts/wiki/parsers/tokens_json.py.doc.md` | `scripts/wiki/parsers/tokens_json.py` | да |
| `scripts/wiki/preview.py.doc.md` | `scripts/wiki/preview.py` | да |
| `scripts/wiki/project_graph_compiler.py.doc.md` | `scripts/wiki/project_graph_compiler.py` | да |
| `scripts/wiki/query.py.doc.md` | `scripts/wiki/query.py` | да |
| `scripts/wiki/sdk_client.py.doc.md` | `scripts/wiki/sdk_client.py` | да |
| `scripts/wiki/system_compiler.py.doc.md` | `scripts/wiki/system_compiler.py` | да |
| `scripts/wiki/utils.py.doc.md` | `scripts/wiki/utils.py` | да |
| `scripts/wizard-check-materials.py.doc.md` | `scripts/wizard-check-materials.py` | да |
| `scripts/wizard.sh.doc.md` | `scripts/wizard.sh` | да |

## Глоссарий

- *reference-map* — карта «кто кого вызывает» по всему репозиторию.
- *usage_class* — классификация файла по тому, откуда на него ссылаются:
  - `active` — есть ≥1 ссылка из исполняемого слоя (агент в `agents/`, команда в `commands/` или `.claude/commands/`, скрипт в `scripts/` или `skills/*/scripts/`, PHP-инклюд mu-плагина, git-хук, ссылка из `SKILL.md`).
  - `doc-only` — упоминание только в документации (`wiki/`, `docs/`, README, `CLAUDE.md`, мета-описания блоков и т.п.).
  - `orphan` — 0 ссылок откуда-либо.
- *кластер* — группа файлов с общим префиксом имени (до первого `-` или `_`).
- *candidate-файл* — файл, попавший в скоуп фазы 0 по одному из Glob-паттернов из playbook'а.
- *входящих ссылок (incoming)* — количество уникальных файлов, ссылающихся на данный.
- *исходящих ссылок (outgoing)* — количество уникальных candidate-файлов, упомянутых в данном.
- *mu-plugin* — must-use plugin WordPress; активирован принудительно.

## Замечания по методологии

1. Поиск ведётся по подстрочному совпадению basename (с границами слова для коротких токенов).
2. Очень общие токены (`init`, `build`, `deploy`, `render`, `check`, `verify`, `cta`, `faq`, `hero`, `trust` и др.) исключены из поиска во избежание массовых false-positive.
3. Динамические PHP-инклюды через переменные (`include $X`) reference-map не покрывает — помечать вручную в фазе 1, если такие будут обнаружены.
4. Категория `style-readme` дала 0 файлов: в `block-library/_styles/*/` фактически лежат `style-guide.md`, а не `README.md` (playbook ожидал второе). Все 6 директорий стилей покрыты через категорию `style-guide`.
5. Скиллы `legal-pages-render` и `wp-builder` содержат только подпапку `scripts/` (без `SKILL.md`) — в категорию `skill` они не попали; их `scripts/` покрыты как `skill-script`.
6. `0 orphan` в результате не означает «всё используется» — а означает, что для каждого candidate-файла нашлась хотя бы одна текстовая отсылка по basename где-то в репо (в т.ч. в `wiki/`). Различение `active` vs `doc-only` показывает реальный вызов из исполняемого слоя — это материал для фазы 1.

## См. также

- Машиночитаемый формат: `phase-0-reference-map.json`
- Пары с пересекающимся scope: `phase-0-suspicious-duplicates.md`
