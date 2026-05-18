---
type: agent
name: ux-composer
sources: ["agents/ux-composer.md"]
updated: 2026-05-15
triggers: []
stage: "07a"
uses: ["prototype-importer", "block-library-management", "block-composer", "wireframe-rendering", "ui-ux-pro-max", "design-tokens-generation", "brand-kit-build"]
tags: ["wireframe", "ux", "stage-07a", "block-library"]
---

# UX Composer — интерактивный вайрфрейм по прототипу

## Что делает

Превращает утверждённый прототип (`prototype.yaml`) в интерактивный `wireframe.html`: для каждого блока страницы предлагает 2–3 варианта компоновки с radio-переключателями. Маркетолог выбирает нужные варианты и скачивает `selections.yaml` для передачи в следующий этап.

## Когда вызывать / в каком этапе

Этап **07a (UX Wireframe)**. Вызывается командой `/landing-wireframe` или агентом `landing-orchestrator`. Требует, чтобы были готовы:
- `07_ПРОТОТИП/prototype.yaml` (этап 07 завершён)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` (этап 05 завершён)
- `04_БРЕНД/brand-kit.md` (этап 04 завершён)
- Плагин `ui-ux-pro-max` с CSV-файлами UX-паттернов, цветов, шрифтов и стилей

Если плагин `ui-ux-pro-max` не установлен — агент немедленно останавливается и выводит инструкцию по установке.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — структурированный прототип
- `block-library/catalog.yaml` — каталог доступных блоков
- `04_БРЕНД/brand-kit.md`, `05_ДИЗАЙН-СИСТЕМА/tokens.json` — бренд и токены
- 6 CSV-файлов из `ui-ux-pro-max` (UX-паттерны, правила, цвета, шрифты, стили)
- 2–3 DESIGN.md reference из `vendor/opendesign-extracts/`

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный вайрфрейм с вариантами блоков
- `07a_WIREFRAME/candidates.yaml` — кандидаты блоков с UX-мета
- `07a_WIREFRAME/selections.yaml` — выбор пользователя (создаётся вручную через UI)

## Ключевые правила

1. **Никогда не придумывает блоки**: если в `block-library` нет подходящего блока для секции прототипа — возвращает `needs_new_block: true` и предлагает создать блок через `scaffold-block.py`.
2. **HARD GATE**: следующий этап (07b Compose) недоступен, пока `selections.yaml` не появится в папке `07a_WIREFRAME/`.
3. UX-правила из CSV инжектируются в wireframe.html как вкладки (`{{ux_patterns_html}}`, `{{ux_rules_html}}` и т.д.) — маркетолог видит рекомендации прямо в браузере.

## Связанные концепты

- [[prototype-importer]] — создаёт `prototype.yaml`, который является входом для ux-composer
- [[block-library-management]] — хранит каталог блоков; ux-composer выбирает только из него
- [[block-composer]] — следующий этап: берёт `selections.yaml` и рендерит `composed.html`
- [[wireframe-rendering]] — скилл, содержащий скрипт `render-wireframe.py` и шаблон `wireframe-shell.html`
- ui-ux-pro-max — обязательная зависимость с CSV-данными UX-паттернов и палитр
- [[landing-orchestrator]] — вызывает ux-composer в рамках общего workflow

## Источник

- `agents/ux-composer.md`