---
slug: stage-08-spec-lint
type: rule
name: "Stage-08 Composed ↔ block-spec Lint"
stage: "08"
tags: [lint, stage-08, block-spec, gate, quality, composed]
triggers: [landing-build]
inputs: [07b_COMPOSED/composed.html, 08_КОД/block-spec.yaml]
outputs: [lint-report-json, exit-code]
gates: [stage-08-spec-lint]
pre_reqs: [landing-compose, landing-build]
related: [landing-build, landing-style, landing-compose, wp-gutenberg-block-builder]
sources: ["docs/standards/stage-08-spec-lint.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Stage-08 Composed ↔ block-spec Lint

## Что делает

Линтер сверяет `07b_COMPOSED/composed*.html` с декларацией блоков в `08_КОД/block-spec.yaml` и обнаруживает расхождения между визуальным HTML и схемой контролей Lazy Blocks. Проверяются пять классов несоответствий: количество буллетов относительно text-field-контролей, наличие color-swatch при отсутствующем controls-color, количество параграфов в textarea, количество картинок в слайдере и наличие SVG-иконок без непустого `icon_svg`. Скрипт запускается автоматически через `scripts/gate-check.sh` и является обязательным условием закрытия этапа 08.

## Когда вызывается

Запускается автоматически при проверке gate этапа 08 через `gate-check.sh`. Может быть вызван вручную командой `python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py --project <path>`. Флаг `--fix` активирует авто-исправление многоабзацных textarea; флаг `--json` выдаёт машино-читаемый результат для CI-интеграции.

## Вход → выход

**Вход:** собранный `composed.html` из этапа 07b и `block-spec.yaml` из этапа 08 с заполненными полями `probe_selector` для каждого блока.

**Выход:** stdout с перечнем ошибок/предупреждений и код выхода: `0` — всё в норме, не-`0` — есть несоответствия. При `--json` — структурированный JSON для программного потребления.

## Failure modes

- **`probe_selector` отсутствует** — блок пропускается с предупреждением; ошибки в нём не обнаруживаются, создаётся ложное ощущение чистоты.
- **`card_probe_selector` не задан для секций** — эвристики `bullets`/`multi-paragraph` сканируют всю секцию целиком, раздувают счётчики и генерируют ложные позитивы.
- **Декоративная карточка не исключена через `card_skip_selector`** — линтер считает её template-экземпляром и сообщает о фантомном `template[N]` overflow.
- **`target_selector` контрола не совпадает с DOM** — проверка молча пропускается, реальная проблема остаётся незамеченной.
- **SVG-поля проверяются как многоабзацный текст** — без whitelist `icon_svg`/`svg`/`background_svg` линтер ошибочно сообщает о несовпадении количества параграфов в SVG-разметке.

## Related

- [[landing-compose]] — генерирует `composed.html`, который является входом линтера
- [[landing-build]] — этап 08, в гейте которого запускается этот линтер
- [[landing-style]] — параллельный этап 08b, работающий с теми же блоками
- [[wp-gutenberg-block-builder]] — скилл, содержащий скрипт линтера и `block-spec.yaml`