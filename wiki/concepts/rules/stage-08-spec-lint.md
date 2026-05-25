---
type: rule
name: stage-08-spec-lint
sources: ["docs/standards/stage-08-spec-lint.md"]
updated: 2026-05-25
triggers: []
stage: "08"
uses: ["landing-build", "landing-compose", "landing-orchestrator"]
tags: ["lint", "stage-08", "block-spec", "composed", "gate"]
---

# Stage-08 Spec Lint — проверка соответствия composed.html и block-spec

## Что делает

Сравнивает готовый HTML-макет (`composed.html`) с декларацией блоков (`block-spec.yaml`) и выявляет несоответствия: лишние или недостающие поля, иконки, изображения, абзацы. Не даёт перейти к сборке WordPress-темы до тех пор, пока HTML и spec не синхронизированы.

## Когда вызывать / в каком этапе

Автоматически запускается через `scripts/gate-check.sh` при закрытии **этапа 08** (landing-build). Stage-08 не может быть помечен как завершённый, пока линтер не вернёт `exit 0`. Можно также вызвать вручную в любой момент после появления `composed.html` и `block-spec.yaml`.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed*.html` — итоговый HTML-макет с реальным контентом
- `08_КОД/block-spec.yaml` — YAML-спецификация всех Lazy Blocks блоков с полями управления (`controls`)

**Выход:**
- Терминальный отчёт об ошибках и предупреждениях
- `--json` — машиночитаемый JSON для интеграции с оркестратором
- `--fix` — автоматическое исправление проблем с многострочными textarea (multi-paragraph extraction)

**Что проверяется:**
1. **Bullets** — количество `<li>` совпадает с количеством text-полей в spec
2. **Color swatches** — наличие `[style*="--c"]` требует контрола `colors`
3. **Multi-paragraph** — количество `<p>` соответствует числу `\n\n`-разделённых абзацев в default-значении
4. **Slider images** — `.slider-track > img` совпадают с `photoN`-полями
5. **Inline SVG icons** — каждый `.feature-icon > svg` требует непустого поля `icon_svg`

**Ключевые настройки в block-spec.yaml:**
- `probe_selector` — обязательный CSS-селектор блока; без него блок пропускается с warning
- `probe_kind: card-collection` + `card_probe_selector` — разбивает проверку по карточкам внутри секции, исключает ложные срабатывания
- `card_skip_selector` — исключает декоративные карточки из подсчёта
- `target_selector` на контроле — сужает зону поиска `<p>` до конкретного суб-элемента

## Связанные концепты

- [[landing-build]] — этап 08, на котором gate вызывает линтер
- [[landing-compose]] — этап 07b, который производит `composed.html`
- [[landing-orchestrator]] — управляет gate-check и блокирует переход этапа

## Источник

- `docs/standards/stage-08-spec-lint.md`