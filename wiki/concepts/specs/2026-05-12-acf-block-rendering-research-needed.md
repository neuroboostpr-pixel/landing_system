---
type: rule
name: acf-block-rendering-research
sources: ["docs/superpowers/specs/2026-05-12-acf-block-rendering-research-NEEDED.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-builder", "wp-gutenberg-block-builder", "wp-cli-deployer", "landing-build"]
tags: ["acf", "lazy-blocks", "gutenberg", "stage-08", "wordpress", "migration"]
---

# ACF Block Rendering — Исследование и миграция на Lazy Blocks

## Что делает
Документирует корневую причину неработающего редактирования блоков в Гутенберге и закрепляет архитектурное решение: отказ от ACF в пользу **Lazy Blocks** для всего stage-08 пайплайна.

## Когда вызывать / в каком этапе
Актуально при генерации WordPress-темы на **этапе 08** (сборка). Применяется автоматически через обновлённые генераторы. Также читать при отладке пустого рендера блоков `do_blocks()` или регрессии «менеджер не видит блок в Гутенберге».

## Что на вход / на выход

**Вход:** `final-copy.md`, `block-spec.yaml` (описание блоков проекта), `tokens.json`.

**Выход:**
- `theme/blocks/lazyblock-<slug>/block.php` — рендер-шаблоны для Lazy Blocks
- `functions.php` — регистрация блоков через хук `lzb/init` → `lazyblocks()->add_block()`
- `assets/css/main.css` — патч `display: contents` для section+card пар
- Lazy Blocks устанавливается через `wp plugin install lazy-blocks --activate` вместо ACF

**Корневая причина (доказана на продакшне):** `acf_register_block_type()` — Pro-only API. ACF Free 6.8.0 игнорирует секцию `"acf": { "renderTemplate": ... }` в `block.json`, поэтому `do_blocks()` возвращает пустую строку для всех блоков `<!-- wp:acf/lp-... -->`.

**Ключевые нюансы Lazy Blocks API:**
- Хук регистрации — исключительно `lzb/init` (не `init`, не `plugins_loaded`)
- Namespace slug — обязательно `lazyblock/<name>`, папка шаблона — `blocks/lazyblock-<name>/block.php`
- `controls` — плоский массив; дочерние контролы repeater'а ссылаются через `child_of` на **ключ** родителя (не на `name`)
- Зарезервированные имена: `anchor`, `lazyblock`, `className`, `blockId` — не использовать в controls
- Сложные блоки разбиваются на пару **section + card** через InnerBlocks, если требуется вложенный repeater

**Удалены:** `generate-acf.py`, `generate-block-json.py`, `generate-block-registration.py`, `front-page.php` writer.  
**Добавлены:** `generate-lzb-registration.py`, `generate-lzb-templates.py`, `generate-css-patches.py`, `generate-page-content.py`.

## Связанные концепты
- [[wp-builder]] — агент stage-08, использует новые генераторы после миграции
- [[wp-gutenberg-block-builder]] — скилл, переписан под Lazy Blocks API
- [[wp-cli-deployer]] — скилл, deploy.sh заменяет ACF на Lazy Blocks при установке
- [[landing-build]] — команда, запускает полный stage-08 с новым пайплайном
- [[08-kod]] — этап сборки, в котором применяется это решение

## Источник
- `docs/superpowers/specs/2026-05-12-acf-block-rendering-research-NEEDED.md`