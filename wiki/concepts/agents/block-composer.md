---
slug: block-composer
type: agent
name: "Block Composer — сборщик composed.html"
stage: "07b"
tags: [compose, html, premium, reference-driven, collage, prototype, tokens]
triggers: [landing-compose]
inputs:
  - 07-prototip
  - 05-dizayn-sistema
  - block-library
  - premium-07b-checklist
outputs:
  - 07b-composed
gates:
  - composed_premium_standard
  - collage_depth
  - tokens_only_colors
  - content_preserved
  - no_invented_text
  - structure_check_md
  - collage_plan_exists
  - block_transitions
pre_reqs:
  - 07-prototip
  - 05-dizayn-sistema
  - 06-stek
related:
  - landing-compose
  - premium-07b-checklist
  - stage-execution-protocol
  - prototype-import
  - 07c-photos
  - 07d-visuals
sources: ["agents/block-composer.md"]
updated: 2026-06-19
---

# Block Composer — сборщик composed.html

## Что делает

Агент вручную рисует полный HTML-макет лендинга по двум источникам правды: `prototype.yaml` (структура блоков и тексты 1:1) и `tokens.json` (цвета, шрифты, характер из дизайн-системы клиента). Reference-driven flow: никакой машинной склейки из библиотеки — агент сам строит коллажную компоузицию с глубиной (наезжающие слои, крупные цифры, формы, движение). Итог — `07b_COMPOSED/composed.html` с реальными текстами, CSS-токенами и именованными placeholders для фото/иконок, которые заполнит PR-B/PR-C.

## Когда вызывается

Запускается скиллом `/landing-compose` (этап 07b), когда `.landing-state.yaml` показывает `current_stage == 07c_composed` и закрыты предшественники: прототип разобран (07a), дизайн-система готова (05). Также триггерится через `/landing-go`, если оркестратор определяет, что этап 07b ещё не начат.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.yaml` (блоки, порядок, тексты, CTA) + `05_ДИЗАЙН-СИСТЕМА/tokens.json` (CSS-переменные, шрифты, палитра) + `block-library/_styles/` (опциональные mood-палитры) + описание правил из `docs/standards/`.

**Выход:** `07b_COMPOSED/composed.html` (полный макет, 13 обязательных премиум-фич), `composed-mobile-preview.html` (iframe iPhone/iPad), `structure-check.md` (заканчивается строкой `STRUCTURE_MATCH: PASS`), `collage-plan.md` (поблочный анализ), `composed-explained.md` (RU-описание принятых решений). При наличии отклонений от прототипа — `.stage-decisions/07b_composed.md`.

## Failure modes

- **Галлюцинация структуры** — агент добавляет блок или элемент, которого нет в `prototype.yaml`; гейт `no_invented_text` / `structure_check_md` не пройдёт.
- **Копирование раскладки прототипа** — CSS подгоняется под скриншот прототипа вместо собственного дизайна из tokens; нарушает §1.2 reference-driven-rules.
- **Прямые цвета вне `:root`** — `verify_tokens.py` падает, гейт `tokens_only_colors` блокирует закрытие этапа.
- **Неполный премиум** — одна или несколько из 13 обязательных фич отсутствуют; `verify-composed-premium.sh` возвращает ненулевой exit code, HARD GATE не проходит.
- **Изменение текста прототипа без разрешения** — `verify-content-preserved.sh` обнаруживает расхождение, этап не закрывается.

## Related

- [[landing-compose]] — скилл-точка входа, диспатчит этот агент
- [[premium-07b-checklist]] — definition of done (13 фич, анти-паттерны)
- [[stage-execution-protocol]] — обязательный протокол pre-flight для всех этапов
- [[prototype-import]] — поставляет `prototype.yaml` на вход
- [[07c-photos]] — следующий этап, заполняет фото-placeholders
- [[07d-visuals]] — параллельный этап, генерирует иконки/инфографику