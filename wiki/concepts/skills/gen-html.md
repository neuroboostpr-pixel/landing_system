---
slug: gen-html
type: skill
name: "Генератор composed.html (gen-html)"
stage: "07c"
tags: [html, compose, reference-driven, moods, design-system, collage]
triggers: [landing-compose]
inputs: [07b-composed, 07-prototip, 05-dizayn-sistema]
outputs: [07b-composed]
pre_reqs: [05-dizayn-sistema, 07-prototip, landing-compose]
related: [landing-compose, landing-visuals, 07b-composed, 05-dizayn-sistema, 07-prototip, premium-07b-checklist]
sources: ["skills/gen-html/SKILL.md"]
updated: 2026-06-22
confidence: {triggers: low}
---

# Генератор composed.html (gen-html)

## Что делает

Скилл рисует `composed.html` с нуля по цепочке трёх источников: ТЗ из `build-spec.md` (mapping контент↔роль), дизайн-система из `moods/*/` (вид-токены, объекты, раскладки), активный прототип (контент дословно). Поддерживает неограниченное число мудов — каждый реализован как отдельная раскладка под `html[data-mood]`, не просто перекраска. Все цвета и размеры идут строго через CSS-переменные, хексы вне палитры запрещены. В итоге появляются `composed.html` и `composed-mobile.html` с встроенным движком (`html-engine.js`) и панелью переключения мудов.

## Когда вызывается

Запускается внутри этапа **07c** (`landing-compose`) после того, как утверждены этап 05 (дизайн-система с мудами) и активный прототип (`meta.active: true`). Агент запускает скрипт `roles-to-css.py` для генерации `objects.css` per-mood, затем верстает блоки по инструкциям прототипа. Перед завершением вызывает `gen-images` для вставки фото и иконок — голые плейсхолдеры на финале не допускаются.

## Вход → выход

**Вход:**
- `07b_COMPOSED/build-spec.md` — ТЗ (mapping ролей, инструкции блоков)
- `07_ПРОТОТИП/prototype-*.yaml` с `meta.active: true` — контент и структура
- `05_ДИЗАЙН-СИСТЕМА/moods/*/` — `objects.yaml`, `palette/typography/motion/metrics.css`, `compositions/*.yaml`

**Выход:**
- `07b_COMPOSED/composed.html` — финальный макет со всеми мудами, движком и панелью-переключателем
- `07b_COMPOSED/composed-mobile.html` — мобильная версия

## Чем закрывается этап (gates)

- `verify_tokens.py` — ноль голых хексов вне palette.css
- `verify_html_vs_ds.py` — размеры через токены; роли из composition реализованы; ровно один активный прототип
- `verify-composed-premium.sh` — движение (IO/@keyframes), `prefers-reduced-motion`, коллажная глубина
- `verify_no_invented_text.py` + `verify-content-preserved.sh` — тексты из прототипа, ничего не выдумано

## Failure modes

- **Активный прототип выбран по имени, не по `meta.active`** — контент берётся из неверного файла, структура расходится с утверждённой
- **Вид объекта переопределён «своим» CSS** — контур превращается в заливку, вырез в бокс; `verify_html_vs_ds.py` ловит, но визуально уже сломано
- **Голый placeholder на финале** — пустая серая плашка вместо фото/иконки; этап не закрывается (гейт `verify-composed-premium.sh`)
- **Моды отличаются только цветом** — раскладка под `[data-mood]` не реализована отдельно; панель мудов теряет смысл
- **Контент первого экрана под `.reveal`** — виден только после скролла; нарушение стандарта §7 п.8

## Related

- [[landing-compose]] — этап 07c, в рамках которого вызывается скилл
- [[07b-composed]] — папка-выход: `build-spec.md` (вход) и `composed.html` (выход)
- [[05-dizayn-sistema]] — источник мудов, объектов, токенов и compositions
- [[07-prototip]] — источник активного прототипа с контентом и `block_instructions`
- [[landing-visuals]] — следующий шаг после gen-html: вставка AI-иконок и инфографики
- [[premium-07b-checklist]] — чеклист качества composed.html, проверяется гейтами