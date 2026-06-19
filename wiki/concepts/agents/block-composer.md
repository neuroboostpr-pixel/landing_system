---
slug: block-composer
type: agent
name: "Block Composer — сборка composed.html"
stage: "07b"
tags: [compose, html, design-tokens, prototype, premium, reference-driven]
triggers: [landing-compose]
inputs: [07-prototip, 05-dizayn-sistema]
outputs: [07b-composed]
gates: [composed_premium_standard, collage_depth, tokens_only_colors, content_preserved, no_invented_text, structure_check_md, collage_plan_exists, block_transitions]
pre_reqs: [07-prototip, 05-dizayn-sistema]
related: [landing-compose, premium-07b-checklist, stage-execution-protocol, 07c-photos, 07d-visuals, landing-prototype, design-system-generator]
sources: ["agents/block-composer.md"]
updated: 2026-06-19
---

# Block Composer — сборка composed.html

## Что делает

Агент этапа 07b: рисует `07b_COMPOSED/composed.html` и `composed-mobile.html` по правилу трёх источников — структура 1:1 из `prototype.yaml`, вид из `tokens.json` (выведен из референса клиента), композиционная глубина из правил коллажа. Работает в reference-driven режиме: не подбирает готовые блоки из библиотеки, а строит макет вручную. Подставляет реальные тексты и CTA из прототипа; фото, иконки и инфографика остаются видимыми плейсхолдерами для PR-B/PR-C. По завершении запускает `verify-composed-premium.sh` и формирует `structure-check.md` с итогом `STRUCTURE_MATCH: PASS`.

## Когда вызывается

Вызывается командой `/landing-compose` внутри папки проекта. Условие: `.landing-state.yaml` должен показывать `current_stage == 07c_composed`; этапы 07-prototip и 05-dizayn-sistema должны быть закрыты. Если предусловия не выполнены — агент останавливается и сообщает об этом.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.yaml` (структура, тексты, CTA), `05_ДИЗАЙН-СИСТЕМА/tokens.json` (цвета, шрифты, характер из референса), `docs/standards/premium-07b-checklist.md` и `docs/standards/reference-driven-rules.md`.

**Выход:** `07b_COMPOSED/composed.html` (полный цветной макет, 13 premium-фич), `composed-mobile.html` (адаптив), `composed-mobile-preview.html` (iframe для глазной проверки), `collage-plan.md` (поблочный анализ глубины), `structure-check.md` (сверка с прототипом, заканчивается `STRUCTURE_MATCH: PASS`), `composed-explained.md` (описание решений на русском).

## Чем закрывается этап (gates)

- `composed_premium_standard` — `verify-composed-premium.sh` возвращает exit 0 (все 13 фич присутствуют)
- `collage_depth` — `verify_collage_depth.py` фиксирует ≥5/6 приёмов глубины
- `tokens_only_colors` — `verify_tokens.py` находит 0 прямых цветов вне `:root`
- `content_preserved` — `verify-content-preserved.sh` подтверждает сохранность всех текстов прототипа
- `no_invented_text` — `verify_no_invented_text.py` не находит выдуманных слов
- `structure_check_md` — `structure-check.md` заканчивается строкой `STRUCTURE_MATCH: PASS`
- `collage_plan_exists` — файл `collage-plan.md` существует и непуст
- `block_transitions` — `verify-block-transitions.py` подтверждает единые переходы между секциями

## Failure modes

- **Галлюцинация структуры** — агент добавляет блок или элемент, которого нет в прототипе; гейт `no_invented_text` / `structure_check_md` заблокирует закрытие этапа.
- **Копирование раскладки прототипа** — CSS повторяет визуальный скриншот прототипа вместо своего дизайна; нарушает §1.2 reference-driven-rules, внешне незаметно до ревью.
- **Пропуск premium-фич** — одна из 13 обязательных фич отсутствует; `verify-composed-premium.sh` вернёт ненулевой exit-код, HARD GATE не пройдён.
- **Прямые цвета вне `:root`** — хардкод `#hex` вместо CSS-переменных; ломает переключение mood-палитр, гейт `tokens_only_colors` упадёт.
- **Запуск на неправильном этапе** — `current_stage` в `.landing-state.yaml` не соответствует `07c_composed`; `enforce_stage_gate.py` физически заблокирует Write/Edit.

## Related

- [[landing-compose]] — slash-команда, запускающая этот агент
- [[premium-07b-checklist]] — definition of done: 13 обязательных фич
- [[stage-execution-protocol]] — обязательный протокол pre-flight для всех этапов
- [[07b-composed]] — этап pipeline, который закрывает этот агент
- [[07c-photos]] — следующий этап: подстановка реальных фото вместо плейсхолдеров (PR-B)
- [[07d-visuals]] — параллельный этап: AI-генерация иконок и инфографики (PR-C)
- [[landing-prototype]] — предшественник: импорт и нормализация прототипа клиента
- [[design-system-generator]] — предшественник: генерация tokens.json из референса